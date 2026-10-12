// SPDX-License-Identifier: MIT
pragma solidity 0.8.17;

import { ERC721SeaDrop } from "seadrop/ERC721SeaDrop.sol";

import {
    MerkleProof
} from "openzeppelin-contracts/utils/cryptography/MerkleProof.sol";

/**
 * @title  WeirdCats
 * @notice Weird Cats collection on Robinhood Chain.
 *
 *         Two ways to mint, sharing one supply:
 *         - SeaDrop (OpenSea drops): inherited from ERC721SeaDrop. The owner
 *           allows the SeaDrop contract and configures the drop in Studio.
 *         - Native mint (weirdcats.xyz or any launchpad frontend): an
 *           allowlist stage (Merkle proof) and a public stage, each with
 *           its own price, time window and per-wallet limit.
 *
 *         Native mint proceeds stay in this contract until `withdraw`
 *         sends them to the payout address.
 */
contract WeirdCats is ERC721SeaDrop {
    /// @notice Price, time window and per-wallet limit of a native stage.
    /// @dev    A stage with `endTime == 0` is closed.
    struct MintStage {
        uint80 price;
        uint48 startTime;
        uint48 endTime;
        uint16 maxPerWallet;
    }

    /// @notice Allowlist stage of the native mint.
    MintStage public allowlistStage;

    /// @notice Public stage of the native mint.
    MintStage public publicStage;

    /// @notice Merkle root of allowlisted wallets.
    /// @dev    Leaves follow OpenZeppelin's StandardMerkleTree format for a
    ///         single `address` value: keccak256(keccak256(abi.encode(addr))).
    bytes32 public allowlistMerkleRoot;

    /// @notice Emergency stop for the native mint. SeaDrop has its own.
    bool public nativeMintPaused;

    /// @notice Receives native mint proceeds on `withdraw`.
    address public payoutAddress;

    /// @notice Tokens each wallet minted in the native allowlist stage.
    mapping(address => uint256) public allowlistMinted;

    /// @notice Tokens each wallet minted in the native public stage.
    mapping(address => uint256) public publicMinted;

    event AllowlistStageUpdated(MintStage stage);
    event PublicStageUpdated(MintStage stage);
    event AllowlistMerkleRootUpdated(bytes32 root);
    event NativeMintPausedUpdated(bool paused);
    event PayoutAddressUpdated(address payoutAddress);
    event Withdrawn(address payoutAddress, uint256 amount);

    error NativeMintPaused();
    error StageNotActive();
    error InvalidQuantity();
    error IncorrectPayment(uint256 got, uint256 want);
    error ExceedsMaxPerWallet(uint256 total, uint256 allowed);
    error InvalidProof();
    error InvalidStageWindow();
    error ZeroPayoutAddress();
    error NothingToWithdraw();
    error WithdrawFailed();

    constructor(
        string memory name,
        string memory symbol,
        address[] memory allowedSeaDrop,
        address initialPayoutAddress
    ) ERC721SeaDrop(name, symbol, allowedSeaDrop) {
        if (initialPayoutAddress == address(0)) revert ZeroPayoutAddress();
        payoutAddress = initialPayoutAddress;
        emit PayoutAddressUpdated(initialPayoutAddress);
    }

    // ------------------------------------------------------------------
    // Native mint
    // ------------------------------------------------------------------

    /// @notice Mint during the allowlist stage.
    /// @param  quantity Number of tokens to mint.
    /// @param  proof    Merkle proof that `msg.sender` is allowlisted.
    function mintAllowlist(uint256 quantity, bytes32[] calldata proof)
        external
        payable
        nonReentrant
    {
        bytes32 leaf = keccak256(
            bytes.concat(keccak256(abi.encode(msg.sender)))
        );
        if (!MerkleProof.verifyCalldata(proof, allowlistMerkleRoot, leaf)) {
            revert InvalidProof();
        }

        uint256 minted = allowlistMinted[msg.sender] + quantity;
        _checkNativeMint(allowlistStage, quantity, minted);
        allowlistMinted[msg.sender] = minted;

        _safeMint(msg.sender, quantity);
    }

    /// @notice Mint during the public stage.
    /// @param  quantity Number of tokens to mint.
    function mintPublic(uint256 quantity) external payable nonReentrant {
        uint256 minted = publicMinted[msg.sender] + quantity;
        _checkNativeMint(publicStage, quantity, minted);
        publicMinted[msg.sender] = minted;

        _safeMint(msg.sender, quantity);
    }

    /// @notice Owner mint for the team reserve, giveaways and airdrops.
    ///         Ignores stages, prices and the pause, but not the max supply.
    function ownerMint(address to, uint256 quantity)
        external
        onlyOwner
        nonReentrant
    {
        if (quantity == 0) revert InvalidQuantity();
        _checkMaxSupply(quantity);
        _safeMint(to, quantity);
    }

    function _checkNativeMint(
        MintStage memory stage,
        uint256 quantity,
        uint256 walletTotal
    ) internal view {
        if (nativeMintPaused) revert NativeMintPaused();
        if (
            block.timestamp < stage.startTime ||
            block.timestamp >= stage.endTime
        ) {
            revert StageNotActive();
        }
        if (quantity == 0) revert InvalidQuantity();
        if (walletTotal > stage.maxPerWallet) {
            revert ExceedsMaxPerWallet(walletTotal, stage.maxPerWallet);
        }
        uint256 cost = uint256(stage.price) * quantity;
        if (msg.value != cost) revert IncorrectPayment(msg.value, cost);
        _checkMaxSupply(quantity);
    }

    function _checkMaxSupply(uint256 quantity) internal view {
        if (_totalMinted() + quantity > maxSupply()) {
            revert MintQuantityExceedsMaxSupply(
                _totalMinted() + quantity,
                maxSupply()
            );
        }
    }

    // ------------------------------------------------------------------
    // Owner configuration
    // ------------------------------------------------------------------

    function setAllowlistStage(MintStage calldata stage) external onlyOwner {
        _checkStageWindow(stage);
        allowlistStage = stage;
        emit AllowlistStageUpdated(stage);
    }

    function setPublicStage(MintStage calldata stage) external onlyOwner {
        _checkStageWindow(stage);
        publicStage = stage;
        emit PublicStageUpdated(stage);
    }

    function setAllowlistMerkleRoot(bytes32 root) external onlyOwner {
        allowlistMerkleRoot = root;
        emit AllowlistMerkleRootUpdated(root);
    }

    function setNativeMintPaused(bool paused) external onlyOwner {
        nativeMintPaused = paused;
        emit NativeMintPausedUpdated(paused);
    }

    function setPayoutAddress(address newPayoutAddress) external onlyOwner {
        if (newPayoutAddress == address(0)) revert ZeroPayoutAddress();
        payoutAddress = newPayoutAddress;
        emit PayoutAddressUpdated(newPayoutAddress);
    }

    /// @notice Send the native mint proceeds to the payout address.
    ///         Anyone can call it; the funds only go to `payoutAddress`.
    function withdraw() external nonReentrant {
        uint256 amount = address(this).balance;
        if (amount == 0) revert NothingToWithdraw();
        address to = payoutAddress;
        (bool ok, ) = to.call{ value: amount }("");
        if (!ok) revert WithdrawFailed();
        emit Withdrawn(to, amount);
    }

    function _checkStageWindow(MintStage calldata stage) internal pure {
        // endTime == 0 closes the stage; otherwise the window must be valid.
        if (stage.endTime != 0 && stage.endTime <= stage.startTime) {
            revert InvalidStageWindow();
        }
    }
}
