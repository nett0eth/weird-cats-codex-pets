// SPDX-License-Identifier: MIT
pragma solidity 0.8.17;

import { Test } from "forge-std/Test.sol";

import { WeirdCats } from "../src/WeirdCats.sol";
import { SeaDrop } from "seadrop/SeaDrop.sol";
import { PublicDrop } from "seadrop/lib/SeaDropStructs.sol";
import {
    ISeaDropTokenContractMetadata
} from "seadrop/interfaces/ISeaDropTokenContractMetadata.sol";

contract WeirdCatsTest is Test {
    WeirdCats internal cats;
    SeaDrop internal seaDrop;

    address internal owner = address(this);
    address internal payout = makeAddr("payout");
    address internal alice = makeAddr("alice");
    address internal bob = makeAddr("bob");
    address internal carol = makeAddr("carol");
    address internal dave = makeAddr("dave");
    address internal feeRecipient = makeAddr("feeRecipient");

    uint256 internal constant MAX_SUPPLY = 20;
    uint80 internal constant PUBLIC_PRICE = 0.002 ether;
    uint80 internal constant ALLOWLIST_PRICE = 0.001 ether;

    bytes32[4] internal leaves;
    bytes32 internal root;

    function setUp() public {
        seaDrop = new SeaDrop();

        address[] memory allowed = new address[](1);
        allowed[0] = address(seaDrop);
        cats = new WeirdCats("Weird Cats", "WCATS", allowed, payout);
        cats.setMaxSupply(MAX_SUPPLY);

        // Allowlist: alice, bob, carol, dave.
        leaves[0] = _leaf(alice);
        leaves[1] = _leaf(bob);
        leaves[2] = _leaf(carol);
        leaves[3] = _leaf(dave);
        root = _hashPair(
            _hashPair(leaves[0], leaves[1]),
            _hashPair(leaves[2], leaves[3])
        );
        cats.setAllowlistMerkleRoot(root);

        vm.deal(alice, 1 ether);
        vm.deal(bob, 1 ether);
        vm.deal(carol, 1 ether);
        vm.deal(dave, 1 ether);
    }

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------

    function _leaf(address account) internal pure returns (bytes32) {
        return keccak256(bytes.concat(keccak256(abi.encode(account))));
    }

    function _hashPair(bytes32 a, bytes32 b) internal pure returns (bytes32) {
        return
            a < b
                ? keccak256(abi.encodePacked(a, b))
                : keccak256(abi.encodePacked(b, a));
    }

    function _proof(uint256 index) internal view returns (bytes32[] memory p) {
        p = new bytes32[](2);
        p[0] = leaves[index ^ 1];
        p[1] = index < 2
            ? _hashPair(leaves[2], leaves[3])
            : _hashPair(leaves[0], leaves[1]);
    }

    function _openPublic(uint16 maxPerWallet) internal {
        cats.setPublicStage(
            WeirdCats.MintStage({
                price: PUBLIC_PRICE,
                startTime: uint48(block.timestamp),
                endTime: uint48(block.timestamp + 1 days),
                maxPerWallet: maxPerWallet
            })
        );
    }

    function _openAllowlist(uint16 maxPerWallet) internal {
        cats.setAllowlistStage(
            WeirdCats.MintStage({
                price: ALLOWLIST_PRICE,
                startTime: uint48(block.timestamp),
                endTime: uint48(block.timestamp + 1 days),
                maxPerWallet: maxPerWallet
            })
        );
    }

    // ------------------------------------------------------------------
    // Deployment
    // ------------------------------------------------------------------

    function testDeployment() public view {
        assertEq(cats.name(), "Weird Cats");
        assertEq(cats.symbol(), "WCATS");
        assertEq(cats.owner(), owner);
        assertEq(cats.payoutAddress(), payout);
        assertEq(cats.maxSupply(), MAX_SUPPLY);
        assertEq(cats.totalSupply(), 0);
    }

    function testRejectsZeroPayoutOnDeploy() public {
        vm.expectRevert(WeirdCats.ZeroPayoutAddress.selector);
        new WeirdCats("Weird Cats", "WCATS", new address[](0), address(0));
    }

    // ------------------------------------------------------------------
    // Public stage
    // ------------------------------------------------------------------

    function testPublicMint() public {
        _openPublic(3);
        vm.prank(alice);
        cats.mintPublic{ value: PUBLIC_PRICE * 2 }(2);

        assertEq(cats.balanceOf(alice), 2);
        assertEq(cats.ownerOf(1), alice);
        assertEq(cats.ownerOf(2), alice);
        assertEq(cats.publicMinted(alice), 2);
        assertEq(address(cats).balance, PUBLIC_PRICE * 2);
    }

    function testPublicMintClosedByDefault() public {
        vm.prank(alice);
        vm.expectRevert(WeirdCats.StageNotActive.selector);
        cats.mintPublic{ value: PUBLIC_PRICE }(1);
    }

    function testPublicMintBeforeStartAndAfterEnd() public {
        uint48 start = uint48(block.timestamp + 1 hours);
        cats.setPublicStage(
            WeirdCats.MintStage({
                price: PUBLIC_PRICE,
                startTime: start,
                endTime: start + 1 hours,
                maxPerWallet: 5
            })
        );

        vm.prank(alice);
        vm.expectRevert(WeirdCats.StageNotActive.selector);
        cats.mintPublic{ value: PUBLIC_PRICE }(1);

        vm.warp(start);
        vm.prank(alice);
        cats.mintPublic{ value: PUBLIC_PRICE }(1);

        vm.warp(start + 1 hours);
        vm.prank(alice);
        vm.expectRevert(WeirdCats.StageNotActive.selector);
        cats.mintPublic{ value: PUBLIC_PRICE }(1);
    }

    function testPublicMintWrongPayment() public {
        _openPublic(3);
        vm.prank(alice);
        vm.expectRevert(
            abi.encodeWithSelector(
                WeirdCats.IncorrectPayment.selector,
                PUBLIC_PRICE,
                uint256(PUBLIC_PRICE) * 2
            )
        );
        cats.mintPublic{ value: PUBLIC_PRICE }(2);
    }

    function testPublicMintWalletLimit() public {
        _openPublic(2);
        vm.startPrank(alice);
        cats.mintPublic{ value: PUBLIC_PRICE * 2 }(2);
        vm.expectRevert(
            abi.encodeWithSelector(
                WeirdCats.ExceedsMaxPerWallet.selector,
                3,
                2
            )
        );
        cats.mintPublic{ value: PUBLIC_PRICE }(1);
        vm.stopPrank();
    }

    function testPublicMintZeroQuantity() public {
        _openPublic(2);
        vm.prank(alice);
        vm.expectRevert(WeirdCats.InvalidQuantity.selector);
        cats.mintPublic(0);
    }

    function testFreeMint() public {
        cats.setPublicStage(
            WeirdCats.MintStage({
                price: 0,
                startTime: uint48(block.timestamp),
                endTime: uint48(block.timestamp + 1 days),
                maxPerWallet: 1
            })
        );
        vm.prank(alice);
        cats.mintPublic(1);
        assertEq(cats.balanceOf(alice), 1);
    }

    function testPause() public {
        _openPublic(3);
        cats.setNativeMintPaused(true);

        vm.prank(alice);
        vm.expectRevert(WeirdCats.NativeMintPaused.selector);
        cats.mintPublic{ value: PUBLIC_PRICE }(1);

        cats.setNativeMintPaused(false);
        vm.prank(alice);
        cats.mintPublic{ value: PUBLIC_PRICE }(1);
    }

    // ------------------------------------------------------------------
    // Allowlist stage
    // ------------------------------------------------------------------

    function testAllowlistMint() public {
        _openAllowlist(2);
        bytes32[] memory proof = _proof(2);

        vm.prank(carol);
        cats.mintAllowlist{ value: ALLOWLIST_PRICE * 2 }(2, proof);

        assertEq(cats.balanceOf(carol), 2);
        assertEq(cats.allowlistMinted(carol), 2);
    }

    function testAllowlistRejectsWrongProof() public {
        _openAllowlist(2);
        bytes32[] memory carolProof = _proof(2);

        // Bob uses Carol's proof.
        vm.prank(bob);
        vm.expectRevert(WeirdCats.InvalidProof.selector);
        cats.mintAllowlist{ value: ALLOWLIST_PRICE }(1, carolProof);

        // Someone outside the list.
        address eve = makeAddr("eve");
        vm.deal(eve, 1 ether);
        vm.prank(eve);
        vm.expectRevert(WeirdCats.InvalidProof.selector);
        cats.mintAllowlist{ value: ALLOWLIST_PRICE }(1, carolProof);
    }

    function testAllowlistWalletLimitIsSeparateFromPublic() public {
        _openAllowlist(1);
        _openPublic(1);
        bytes32[] memory proof = _proof(0);

        vm.startPrank(alice);
        cats.mintAllowlist{ value: ALLOWLIST_PRICE }(1, proof);
        vm.expectRevert(
            abi.encodeWithSelector(
                WeirdCats.ExceedsMaxPerWallet.selector,
                2,
                1
            )
        );
        cats.mintAllowlist{ value: ALLOWLIST_PRICE }(1, proof);
        cats.mintPublic{ value: PUBLIC_PRICE }(1);
        vm.stopPrank();

        assertEq(cats.balanceOf(alice), 2);
    }

    // ------------------------------------------------------------------
    // Supply, owner mint, withdraw
    // ------------------------------------------------------------------

    function testOwnerMintAndMaxSupply() public {
        cats.ownerMint(payout, MAX_SUPPLY - 1);
        assertEq(cats.totalSupply(), MAX_SUPPLY - 1);

        _openPublic(5);
        vm.prank(alice);
        vm.expectRevert(
            abi.encodeWithSignature(
                "MintQuantityExceedsMaxSupply(uint256,uint256)",
                MAX_SUPPLY + 1,
                MAX_SUPPLY
            )
        );
        cats.mintPublic{ value: PUBLIC_PRICE * 2 }(2);

        vm.prank(alice);
        cats.mintPublic{ value: PUBLIC_PRICE }(1);
        assertEq(cats.totalSupply(), MAX_SUPPLY);
    }

    function testWithdraw() public {
        _openPublic(3);
        vm.prank(alice);
        cats.mintPublic{ value: PUBLIC_PRICE * 3 }(3);

        // Anyone can trigger it; funds only go to the payout address.
        vm.prank(bob);
        cats.withdraw();

        assertEq(payout.balance, uint256(PUBLIC_PRICE) * 3);
        assertEq(address(cats).balance, 0);

        vm.expectRevert(WeirdCats.NothingToWithdraw.selector);
        cats.withdraw();
    }

    function testOnlyOwnerCanConfigure() public {
        vm.startPrank(alice);
        vm.expectRevert();
        cats.setPublicStage(
            WeirdCats.MintStage({
                price: 0,
                startTime: 0,
                endTime: 1,
                maxPerWallet: 100
            })
        );
        vm.expectRevert();
        cats.setAllowlistMerkleRoot(bytes32(0));
        vm.expectRevert();
        cats.setNativeMintPaused(true);
        vm.expectRevert();
        cats.setPayoutAddress(alice);
        vm.expectRevert();
        cats.ownerMint(alice, 1);
        vm.expectRevert();
        cats.setMaxSupply(1000);
        vm.stopPrank();
    }

    function testStageWindowValidation() public {
        vm.expectRevert(WeirdCats.InvalidStageWindow.selector);
        cats.setPublicStage(
            WeirdCats.MintStage({
                price: 0,
                startTime: 100,
                endTime: 100,
                maxPerWallet: 1
            })
        );
    }

    // ------------------------------------------------------------------
    // Metadata and royalties
    // ------------------------------------------------------------------

    function testTokenURIAndRoyalties() public {
        cats.ownerMint(alice, 1);

        cats.setBaseURI("ipfs://unrevealed.json");
        assertEq(cats.tokenURI(1), "ipfs://unrevealed.json");

        cats.setBaseURI("ipfs://cid/");
        assertEq(cats.tokenURI(1), "ipfs://cid/1");

        cats.setRoyaltyInfo(
            ISeaDropTokenContractMetadata.RoyaltyInfo({
                royaltyAddress: payout,
                royaltyBps: 500
            })
        );
        (address receiver, uint256 amount) = cats.royaltyInfo(1, 1 ether);
        assertEq(receiver, payout);
        assertEq(amount, 0.05 ether);
    }

    // ------------------------------------------------------------------
    // SeaDrop (OpenSea drops) shares the same supply
    // ------------------------------------------------------------------

    function testSeaDropMintSharesSupply() public {
        cats.updateCreatorPayoutAddress(address(seaDrop), payout);
        cats.updateAllowedFeeRecipient(address(seaDrop), feeRecipient, true);
        cats.updatePublicDrop(
            address(seaDrop),
            PublicDrop({
                mintPrice: PUBLIC_PRICE,
                startTime: uint48(block.timestamp),
                endTime: uint48(block.timestamp + 1 days),
                maxTotalMintableByWallet: 10,
                feeBps: 1000,
                restrictFeeRecipients: true
            })
        );

        cats.ownerMint(payout, MAX_SUPPLY - 2);

        vm.prank(bob);
        seaDrop.mintPublic{ value: PUBLIC_PRICE }(
            address(cats),
            feeRecipient,
            address(0),
            1
        );
        assertEq(cats.balanceOf(bob), 1);

        // Native mint takes the last token.
        _openPublic(5);
        vm.prank(alice);
        cats.mintPublic{ value: PUBLIC_PRICE }(1);
        assertEq(cats.totalSupply(), MAX_SUPPLY);

        // SeaDrop can't go past the max supply either.
        vm.prank(carol);
        vm.expectRevert();
        seaDrop.mintPublic{ value: PUBLIC_PRICE }(
            address(cats),
            feeRecipient,
            address(0),
            1
        );
    }

    function testOnlyAllowedSeaDropCanMint() public {
        vm.prank(alice);
        vm.expectRevert(abi.encodeWithSignature("OnlyAllowedSeaDrop()"));
        cats.mintSeaDrop(alice, 1);
    }
}
