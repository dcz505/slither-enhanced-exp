from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations import Assignment, Binary, Condition
from slither.core.declarations import Contract
from slither.analyses.data_dependency.data_dependency import is_dependent

class UncheckedBalanceChangeDetector(AbstractDetector):
    ARGUMENT = "unchecked-balance-change"
    HELP = "Detects unchecked changes to token balances"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.MEDIUM

    WIKI = "https://github.com/your-repo/wiki/unchecked-balance-change"
    WIKI_TITLE = "Unchecked Token Balance Change"
    WIKI_DESCRIPTION = "Token balance changes without sufficient checks may allow unauthorized modifications."
    WIKI_EXPLOIT_SCENARIO = "A function increases `balances[msg.sender]` without verifying funds."
    WIKI_RECOMMENDATION = "Add require() checks before modifying balances."

    def _detect(self):
        results = []
        # Iterate over all contracts
        for contract in self.slither.contracts:
            # Look for balance-like mappings in state variables
            balance_vars = [v for v in contract.state_variables if "mapping(address=>uint256)" in str(v.type)]
            if not balance_vars:
                continue

            # Analyze each function
            for function in contract.functions:
                for node in function.nodes:
                    # Check for assignments to balance variables
                    for ir in node.irs:
                        if isinstance(ir, Assignment):
                            # Check if left-hand side is a balance variable reference
                            if any(ir.lvalue.name.startswith(var.name) for var in balance_vars):
                                # Look for preceding conditions guarding this assignment
                                has_check = False
                                for parent_node in node.function.nodes:
                                    if parent_node == node:
                                        break
                                    for parent_ir in parent_node.irs:
                                        if isinstance(parent_ir, Condition):
                                            # Check if condition depends on the balance variable
                                            if any(is_dependent(parent_ir.expression, var, contract) for var in balance_vars):
                                                has_check = True
                                                break
                                    if has_check:
                                        break
                                if not has_check:
                                    info = [f"Unchecked balance change in {function.name} ({contract.name})\n"]
                                    results.append(self.generate_result(info))

        return results

# Register the detector
def make_plugin():
    return [UncheckedBalanceChangeDetector]
