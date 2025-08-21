// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import "./IClaimVerifier.sol";
contract SortingClaimVerifier is IClaimVerifier {
    function violates(bytes calldata input, bytes calldata output) external pure returns (bool) {
        uint256[] memory a = abi.decode(input, (uint256[]));
        uint256[] memory out = abi.decode(output, (uint256[]));
        if (out.length != a.length) return true;
        unchecked {
            for (uint256 i=0;i+1<out.length;i++){ if (out[i] > out[i+1]) return true; }
        }
        // Heuristic multiset check for demo (gas-friendly small inputs)
        bytes32 ha=bytes32(0); bytes32 ho=bytes32(0);
        for (uint256 i=0;i<a.length;i++) { ha = keccak256(abi.encodePacked(ha, keccak256(abi.encode(a[i])))); }
        for (uint256 i=0;i<out.length;i++){ ho = keccak256(abi.encodePacked(ho, keccak256(abi.encode(out[i])))); }
        return ha != ho;
    }
}