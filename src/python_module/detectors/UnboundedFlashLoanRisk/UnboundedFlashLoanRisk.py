from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.core.declarations import Function
from slither.analyses.data_dependency.data_dependency import is_tainted
from slither.slithir.operations import Call

class UnboundedFlashLoanRisk(AbstractDetector):
    """
    Detects unbounded state changes in DeFi contracts triggered by flash loan callbacks.
    """

    ARGUMENT = 'unbounded-flashloan-risk'
    HELP = 'Unbounded state changes after flash loan callbacks'
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.MEDIUM

    WIKI = 'https://example.com/wiki/unbounded-flashloan-risk'
    WIKI_TITLE = 'Unbounded Flash Loan Risk'
    WIKI_DESCRIPTION = (
        'Detects functions handling flash loan callbacks that modify critical state '
        'without proper bounds or validation, risking manipulation or exploits.'
    )
    WIKI_EXPLOIT_SCENARIO = (
        'A DeFi contract implements `uniswapV2Call` and updates a price variable based on '
        'flash loan inputs. Without bounds, an attacker manipulates the price via a large loan.'
    )
    WIKI_RECOMMENDATION = (
        'Add explicit bounds or range checks on state variables modified in flash loan callbacks. '
        'Use interval analysis to ensure constraints hold.'
    )

    def _is_flash_loan_callback(self, function: Function) -> bool:
        """Check if function is a flash loan callback (e.g., Uniswap, Aave)."""
        flash_loan_sigs = [
            "uniswapV2Call(address,uint256,uint256,bytes)",
            "executeOperation(address[],uint256[],uint256[],address,bytes)"
        ]
        return function.signature in flash_loan_sigs

    def _has_unbounded_state_change(self, function: Function) -> bool:
        """Check for unbounded state modifications using interval analysis."""
        for ir in function.slithir_operations:
            if isinstance(ir, Call) and ir.function:
                # Check if internal calls modify state without bounds
                for var in ir.function.modified_state_variables:
                    if not var.type.is_bounded and is_tainted(var, function):
                        return True
        return False

    def _detect(self):
        results = []
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                if self._is_flash_loan_callback(function):
                    if self._has_unbounded_state_change(function):
                        info = [
                            f"Function {function.full_name} in contract {contract.name} ",
                            "handles a flash loan callback with unbounded state changes.\n"
                        ]
                        results.append(self.generate_result(info))
        return results
