// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
interface IClaimVerifier {
    function violates(bytes calldata input, bytes calldata output) external view returns (bool);
}