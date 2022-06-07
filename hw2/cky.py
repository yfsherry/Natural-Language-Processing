"""
COMS W4705 - Natural Language Processing
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""
import math
# from operator import length_hint
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the se                                                                             ntence is in the language described by the grammar. Otherwise
        return False
        """
        # TODO, part 2
        rhs_rules = list(self.grammar.rhs_to_rules)
        n = len(tokens)
        table = [[[] for i in range(n+1)] for j in range(n+1)] 

        for i in range(n):
            for rhs in rhs_rules:
                if rhs == (tokens[i],):
                    table[i][i+1] = set()
                    for lhs_rhs_prob in self.grammar.rhs_to_rules[rhs]:
                        table[i][i+1].add(lhs_rhs_prob[0])

        for l in range(2, n+1):
            for i in range(n-l+1):
                j = i + l
                for k in range(i+1, j):
                    if not table[i][j]:
                        table[i][j] = set()
                    for rhs in rhs_rules:
                        if len(rhs) == 2:
                            for hpoint in table[i][k]:
                                for vpoint in table[k][j]:
                                    if hpoint == rhs[0] and vpoint == rhs[1]:
                                        for lhs_rhs_prob in self.grammar.rhs_to_rules[rhs]:
                                            table[i][j].add(lhs_rhs_prob[0])

        # check id S is in (1,n)
        if table[0][n-1]:
            return True

        return False 


    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        # TODO, part 3
        rhs_rules = list(self.grammar.rhs_to_rules)
        n = len(tokens)
        table = dict()
        probs = dict()
        for i in range(n+1):
            for j in range(n+1):
                table[(i,j)] = dict()
        
        for i in range(n+1):
            for j in range(n+1):
                probs[(i,j)] = dict()
        
        for i in range(n):
            for rhs in rhs_rules:
                if rhs == (tokens[i],):
                    table[(i,i+1)] = dict()
                    probs[(i,i+1)] = dict()
                    for lhs_rhs_prob in self.grammar.rhs_to_rules[rhs]:
                        table[(i,i+1)][lhs_rhs_prob[0]] = lhs_rhs_prob[1][0]
                        probs[(i,i+1)][lhs_rhs_prob[0]] = math.log(lhs_rhs_prob[2])
        
        for l in range(2, n+1):
            for i in range(n-l+1):
                j = i + l
                for k in range(i+1, j):
                    if (i,j) not in table.keys():
                        table[(i,j)] = dict()
                        probs[(i,j)] = dict()
                    for rhs in rhs_rules:
                        if len(rhs) == 2:
                            for hpoint in table[(i,k)].keys():
                                for vpoint in table[(k,j)].keys(): 
                                    if hpoint == rhs[0] and vpoint == rhs[1]:
                                        for lhs_rhs_prob in self.grammar.rhs_to_rules[rhs]:
                                            if not lhs_rhs_prob[2] == 0: # probs not 0
                                                nextpoint = ((hpoint, i, k),(vpoint, k, j))
                                                prob = math.log(lhs_rhs_prob[2]) + probs[(i,k)][hpoint] + probs[(k,j)][vpoint]
                                                if lhs_rhs_prob[0] not in probs[(i,j)]:
                                                    table[(i,j)][lhs_rhs_prob[0]] = nextpoint
                                                    probs[(i,j)][lhs_rhs_prob[0]] = prob
                                                else:
                                                    if prob > probs[(i,j)][lhs_rhs_prob[0]]:
                                                        table[(i,j)][lhs_rhs_prob[0]] = nextpoint
                                                        probs[(i,j)][lhs_rhs_prob[0]] = prob
                                            else: # probs be 0
                                                if lhs_rhs_prob[0] not in table[(i,j)]:
                                                    table[(i,j)][lhs_rhs_prob[0]] = ((hpoint, i, k),(vpoint, k,))
                                                    probs[(i,j)][lhs_rhs_prob[0]] = 0
 
        return table, probs


    def get_tree(chart, i,j,nt): 
        """
        Return the parse-tree rooted in non-terminal nt and covering span i,j.
        """
        # TODO: Part 4
        nextpoint = chart[(i,j)][nt]

        if isinstance(nextpoint, str):
            return(nt, nextpoint)
        left = nextpoint[0]
        right = nextpoint[1]
        left_tree = get_tree(chart, left[1], left[2], left[0])
        right_tree = get_tree(chart, right[1], right[2], left[0])


        return (nt, left_tree, right_tree) 



def get_tree(chart, i,j,nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    # TODO: Part 4
    nextpoint = chart[(i,j)][nt]

    if isinstance(nextpoint, str):
        return(nt, nextpoint)
    left = nextpoint[0]
    right = nextpoint[1]
    left_tree = get_tree(chart, left[1], left[2], left[0])
    right_tree = get_tree(chart, right[1], right[2], left[0])

    
    return (nt, left_tree, right_tree) 
 
       
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)
        toks =['flights', 'from','miami', 'to', 'cleveland','.'] 
        print(parser.is_in_language(toks))
        table,probs = parser.parse_with_backpointers(toks)
        assert check_table_format(table)
        assert check_probs_format(probs)
        
