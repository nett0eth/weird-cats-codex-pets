// SPDX-License-Identifier: MIT
pragma solidity 0.8.17;

import { Script, console2 } from "forge-std/Script.sol";

import { WeirdCats } from "../src/WeirdCats.sol";
import {
    ISeaDropTokenContractMetadata
} from "seadrop/interfaces/ISeaDropTokenContractMetadata.sol";

/**
 * @notice Deploys WeirdCats with every mint closed.
 *
 *         Required env:
 *           PAYOUT_ADDRESS  Receives mint proceeds and royalties (use a Safe).
 *           MAX_SUPPLY      Collection size.
 *         Optional env:
 *           SEADROP_ADDRESS SeaDrop contract to allow (default: canonical).
 *           ROYALTY_BPS     Royalty in basis points (default: 500 = 5%).
 *           CONTRACT_URI    Collection metadata JSON (name, image, banner...).
 *           BASE_URI        Token metadata (unrevealed JSON or folder with "/").
 *
 *         Stages start closed (endTime == 0), so nobody can mint until the
 *         owner calls setPublicStage / setAllowlistStage or configures a drop.
 */
contract Deploy is Script {
    address internal constant CANONICAL_SEADROP =
        0x00005EA00Ac477B1030CE78506496e8C2dE24bf5;

    function run() external returns (WeirdCats cats) {
        address payout = vm.envAddress("PAYOUT_ADDRESS");
        uint256 maxSupply = vm.envUint("MAX_SUPPLY");
        address seaDrop = vm.envOr("SEADROP_ADDRESS", CANONICAL_SEADROP);
        uint96 royaltyBps = uint96(vm.envOr("ROYALTY_BPS", uint256(500)));
        string memory contractURI = vm.envOr("CONTRACT_URI", string(""));
        string memory baseURI = vm.envOr("BASE_URI", string(""));

        address[] memory allowedSeaDrop = new address[](1);
        allowedSeaDrop[0] = seaDrop;

        vm.startBroadcast();

        cats = new WeirdCats("Weird Cats", "WCATS", allowedSeaDrop, payout);
        cats.setMaxSupply(maxSupply);
        cats.setRoyaltyInfo(
            ISeaDropTokenContractMetadata.RoyaltyInfo({
                royaltyAddress: payout,
                royaltyBps: royaltyBps
            })
        );
        if (bytes(contractURI).length != 0) cats.setContractURI(contractURI);
        if (bytes(baseURI).length != 0) cats.setBaseURI(baseURI);

        vm.stopBroadcast();

        console2.log("WeirdCats deployed at", address(cats));
        console2.log("Owner", cats.owner());
        console2.log("Max supply", cats.maxSupply());
    }
}
