# Weird Cats contract

`WeirdCats` is an ERC-721A collection for Robinhood Chain. It is built on OpenSea's [SeaDrop](https://github.com/ProjectOpenSea/seadrop) token (`ERC721SeaDrop`). All mint routes share one max supply:

- **OpenSea drops (SeaDrop):** allow the SeaDrop contract, then configure the drop in OpenSea Studio.
- **Native mint (weirdcats.xyz or a launchpad frontend):** an allowlist stage with a Merkle proof and a public stage. Each stage has its own price, time window and per-wallet limit.
- **Owner mint:** for the team reserve and airdrops.

Royalties use ERC-2981. Collection metadata comes from `contractURI`, and token metadata from `baseURI`. A base URI without a trailing `/` returns the same unrevealed JSON for every token.

## Layout

| Path | What it is |
| --- | --- |
| `src/WeirdCats.sol` | The collection contract |
| `test/WeirdCats.t.sol` | Foundry tests, including a real SeaDrop mint sharing the supply |
| `script/Deploy.s.sol` | Deploys the contract with every mint closed |
| `lib/seadrop` | OpenSea SeaDrop, pinned to `757590f` (git submodule) |
| `lib/forge-std` | forge-std `v1.17.0` (git submodule) |

## Build and test

```sh
git submodule update --init --recursive
cd contracts
forge test
```

The compiler is solc `0.8.17`, the same as SeaDrop, with `evm_version = "paris"`.

## Networks

| | Mainnet | Testnet |
| --- | --- | --- |
| Chain ID | `4663` | `46630` |
| RPC | `https://rpc.mainnet.chain.robinhood.com` | `https://rpc.testnet.chain.robinhood.com` |
| Explorer | `https://robinhoodchain.blockscout.com` | `https://explorer.testnet.chain.robinhood.com` |

Source: [Robinhood Chain docs](https://docs.robinhood.com/chain/connecting).

## Deploy

Deploy to testnet first. The deployer wallet becomes the owner. Never put a private key in a file. Use `--ledger` or `--interactive`.

```sh
export RH_RPC_URL=https://rpc.testnet.chain.robinhood.com
export PAYOUT_ADDRESS=0x...   # Safe that receives proceeds and royalties
export MAX_SUPPLY=...         # collection size
export ROYALTY_BPS=500        # 5%
export CONTRACT_URI=ipfs://.../contract.json   # optional
export BASE_URI=ipfs://.../unrevealed.json     # optional

forge script script/Deploy.s.sol --rpc-url $RH_RPC_URL --broadcast --interactive 1
```

Verify on Blockscout. On mainnet, use chain ID `4663` and `https://robinhoodchain.blockscout.com/api/`.

```sh
forge verify-contract <address> src/WeirdCats.sol:WeirdCats \
  --chain-id 46630 --rpc-url $RH_RPC_URL \
  --verifier blockscout --verifier-url https://explorer.testnet.chain.robinhood.com/api/ \
  --constructor-args $(cast abi-encode "constructor(string,string,address[],address)" "Weird Cats" "WCATS" "[0x00005EA00Ac477B1030CE78506496e8C2dE24bf5]" $PAYOUT_ADDRESS)
```

The script allows the canonical SeaDrop address `0x00005EA00Ac477B1030CE78506496e8C2dE24bf5`. Before opening an OpenSea drop, check on the explorer that SeaDrop is deployed on Robinhood Chain at that address. If it lives somewhere else, the owner can change it with `updateAllowedSeaDrop`.

## Opening the mint

After the deploy, every mint is closed. When it is time, the owner opens it:

- **Public:** `setPublicStage((price, startTime, endTime, maxPerWallet))`. Prices are in wei, times are unix seconds, and `endTime = 0` closes the stage.
- **Allowlist:** `setAllowlistMerkleRoot(root)`, then `setAllowlistStage(...)`. Build the tree with [`@openzeppelin/merkle-tree`](https://github.com/OpenZeppelin/merkle-tree) as a `StandardMerkleTree` of `["address"]`.
- **OpenSea drop:** configure it in OpenSea Studio, or call `updatePublicDrop`, `updateCreatorPayoutAddress` and `updateAllowedFeeRecipient` on this contract.
- **Emergency stop for the native mint:** `setNativeMintPaused(true)`. SeaDrop drops are stopped from Studio.
- **Proceeds:** native mint ETH stays in the contract until anyone calls `withdraw()`, which always sends it to `payoutAddress`. SeaDrop pays the creator payout address directly.

SeaDrop's per-wallet limit counts every token a wallet minted, native mints included. The native stages count only their own mints.
