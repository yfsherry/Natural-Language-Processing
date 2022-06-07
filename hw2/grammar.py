"""
COMS W4705 - Natural Language Processing
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""

from cmath import e
import sys
import numpy as np
from collections import defaultdict
from math import fsum


class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """

        """
        Rule constraints:
        - all values in lhs should add up to 1.
        - all nonterminal symbols are upper-case: 
            1. if two values on rhs, then should be no nonterminal with lower-case
            2. if one value on rhs, than this must be terminal in lower-case

        """
        # TODO, Part 1
        for lhs, rhs_probs in self.lhs_to_rules.items():
            probs = []
            for rhs_prob in rhs_probs:
                rhs = rhs_prob[1]
                probs.append(rhs_prob[2])
                if len(rhs) == 1:
                    if not rhs[0].islower():
                        print('rhs with 1 value {} not in lower case for lhs {}'.format(rhs[0], rhs_prob[0]))
                        return False
                elif len(rhs) == 2:
                    if not rhs[0].isupper() or not rhs[1].isupper() or not rhs[0] == '0' or not rhs[1] == '0':
                        print('rhs with 2 values {} {} not in lower case for lhs {}'.format(rhs[0], rhs[1], rhs_prob[0]))
                        return False
                else:
                    return False
            sum_prob = fsum(np.float128(rhs_prob[2]) for rhs_prob in rhs_probs)
            # print(sum_prob)
            if np.abs(1 - sum_prob) > 1e-11:
                print('sum probabiliy of lhs {} is not 1, but {}'.format(lhs, sum_prob))
                print(sum_prob)
                return False
            
        return True


if __name__ == "__main__":
    with open(sys.argv[1],'r') as grammar_file:
        grammar = Pcfg(grammar_file)
        print(grammar.startsymbol)
        print(grammar.lhs_to_rules[grammar.startsymbol])
        if grammar.verify_grammar():
            print('Grammar is a valid PCFG in CNF.')
        else:
            print('Error. Grammar is not valid PCFG in CNF.')
            exit(0)
        
