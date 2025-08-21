// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import "./IClaimVerifier.sol";
contract EvidenceRegistry {
    struct Claim {
        address submitter;
        address verifier;
        bytes32 certHash;
        uint256 bond;
        uint256 deadline;
        bool finalized;
        bool slashed;
    }
    uint256 public nextId;
    mapping(uint256=>Claim) public claims;
    uint256 public immutable window;
    uint256 public immutable minBond;
    event Submitted(uint256 id, address indexed submitter, bytes32 certHash, address verifier, uint256 bond, uint256 deadline);
    event Challenged(uint256 id, address indexed challenger);
    event Slashed(uint256 id, address indexed challenger, uint256 reward);
    event Finalized(uint256 id);
    constructor(uint256 _window, uint256 _minBond){ window=_window; minBond=_minBond; }
    function submit(bytes32 certHash, address verifier) external payable returns (uint256 id){
        require(msg.value>=minBond, "bond");
        id=nextId++;
        claims[id]=Claim(msg.sender, verifier, certHash, msg.value, block.timestamp+window, false, false);
        emit Submitted(id, msg.sender, certHash, verifier, msg.value, block.timestamp+window);
    }
    function challenge(uint256 id, bytes calldata input, bytes calldata output) external {
        Claim storage c=claims[id];
        require(block.timestamp < c.deadline, "over");
        require(!c.finalized && !c.slashed, "closed");
        bool violation = IClaimVerifier(c.verifier).violates(input, output);
        emit Challenged(id, msg.sender);
        if (violation){
            c.slashed = true;
            uint256 reward=c.bond; c.bond=0;
            (bool ok,) = payable(msg.sender).call{value:reward}("");
            require(ok,"xfer");
            emit Slashed(id, msg.sender, reward);
        }
    }
    function finalize(uint256 id) external {
        Claim storage c=claims[id];
        require(block.timestamp>=c.deadline, "early");
        require(!c.finalized, "done");
        c.finalized = true; emit Finalized(id);
    }
    function withdraw(uint256 id) external {
        Claim storage c=claims[id];
        require(c.finalized && !c.slashed, "no");
        require(msg.sender==c.submitter, "auth");
        uint256 amt=c.bond; c.bond=0;
        (bool ok,) = payable(msg.sender).call{value:amt}("");
        require(ok,"xfer");
    }
}