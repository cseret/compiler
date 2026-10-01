# Compiler for a Python like language
# 1st stage - Lexical and Syntax Analyzer
# 2nd stage - Intermediate Code Generation and Symbol Table
# 3rd stage - Final Code Generation in RISC-V Assembly using RARS

# READ ME:
# To run, write to the terminal: 
#            ' python3 compiler.py <filename>.cpy ' 
# for example: python3 compiler.py maintest.cpy

# Tokens for Lexical Analyzer are saved in the file: '<filename>.lex' and can be printed in terminal if hashtag in line 1387 is removed.
# Intermediate code is printed in the terminal and is saved in the file: '<filename>.int'
# Symbol Table is printed in the terminal and saved in the file: '<filename>.symbt'
# Final code is generated in the file: '<filename>.asm' and can be printed in terminal if hashtag in line 1398.

import sys
global line_counter
global pointer
global token
global quadID 
global TempCounter 
global quadList
global Offset
global fclist 
global framelength   

class Token:
    def __init__(self, recognized_string, family, line_number):
        self.recognized_string = recognized_string
        self.family = family
        self.line_number = line_number
        
    def __str__(self):
        return str(self.recognized_string) + " " + str(self.family) + " " + str(self.line_number)

# --- Lexical Analyzer ---- #
class Lex:
    def __init__(self) -> None:
        pass
        
    def isLetter(self, char, line_number):
        sizeofString = 0
        keywords = ["def","#declare","int","input","print","return","if","else","while","or","and","not","__name__",' "__main__"']
        currentWord = ""
        while((char.isalpha() or char.isnumeric() or (char == "_")) and (sizeofString <= 30)):
            currentWord = currentWord + char
            sizeofString = sizeofString + 1
            char = inputfile.read(1)
        if (sizeofString > 30):
            print("Size of word is bigger than 30 characters, at line: " + str(line_number))
            sys.exit(0)
        inputfile.seek(inputfile.tell() - 1)
        if (currentWord in keywords):
            tk = Token(currentWord, "keyword", line_number)
        else:
            tk = Token(currentWord, "identifier", line_number)
        return tk

    def isNumber(self, char, line_number):
        currentNumber = ""
        while(char.isnumeric()):
            currentNumber = currentNumber + char
            char = inputfile.read(1)
        inputfile.seek(inputfile.tell() - 1)
        if ((int(currentNumber) > (4294967296-1))) or (int(currentNumber) < -(4294967296-1)):
            print("Number is out of range at line: " + str(line_number))
            sys.exit(0)
        tk = Token(currentNumber, "number", line_number)
        return tk

    def isAddOperator(self, char, line_number):
        currentAddOperator = char
        tk = Token(currentAddOperator, "addOperator", line_number)
        return tk

    def isMulOperator(self, char, line_number):
        currentMulOperator = char
        if (char == "*"):
            tk = Token(currentMulOperator, "mulOperator", line_number)
        elif (char == "/"):
            char = inputfile.read(1)
            if (char == "/"):
                currentMulOperator = "//"
                tk = Token(currentMulOperator, "mulOperator", line_number)
            else:
                print("Missing second '/' to use division, at line: " + str(line_number))
                sys.exit(0)
        else:
            pass
        return tk

    def isRelOp(self, char, line_number):
        currentRelOp = char
        if (currentRelOp == "<"):
            char = inputfile.read(1)
            if (char == "="):
                currentRelOp = currentRelOp + char
                tk = Token(currentRelOp, "relOperator", line_number)
            else:
                tk = Token(currentRelOp, "relOperator", line_number)
                inputfile.seek(inputfile.tell() - 1)
        elif (currentRelOp == ">"):
            char = inputfile.read(1)
            if (char == "="):
                currentRelOp = currentRelOp + char
                tk = Token(currentRelOp, "relOperator", line_number)
            else:
                tk = Token(currentRelOp, "relOperator", line_number)
                inputfile.seek(inputfile.tell() - 1)
        elif (currentRelOp == "!"):
                char = inputfile.read(1)
                if (char == "="):
                    currentRelOp = currentRelOp + char
                    tk = Token(currentRelOp, "relOperator", line_number)
                else:
                    print("Missing '=' to use '!=' as relOp, at line: " + str(line_number))
                    sys.exit(0)
        else:
            pass
        return tk

    def isAssign(self, char, line_number):
        currentAssign = char
        char = inputfile.read(1)
        if (char == "="):
            currentAssign = currentAssign + char
            tk = Token(currentAssign, "relOperator", line_number)
        else:
            tk = Token(currentAssign, "assignment", line_number)
            inputfile.seek(inputfile.tell() - 1)
        return tk

    def isDelimeter(self, char, line_number):
        currentDelimeter = char
        tk = Token(currentDelimeter, "delimeter", line_number)
        return tk

    def isGroupSymbol(self, char, line_number):
        currentGroupSymbol = char
        tk = Token(currentGroupSymbol, "groupSymbol", line_number)
        return tk

    def isHashtag(self, char, line_number):
        global line_counter
        currentHashtag = char
        char = inputfile.read(1)
        if (char == "{" or char == "}"):
            currentHashtag = currentHashtag + char
            tk = Token(currentHashtag, "groupSymbol", line_number)
        elif (char == "d"):
            currentHashtag = currentHashtag + char
            for i in range(0, 6):
                char = inputfile.read(1)
                currentHashtag = currentHashtag + char
            if (currentHashtag == "#declare"):
                tk = Token(currentHashtag, "keyword", line_number)
            else:
                print("Missing 'declare' to use '#declare', at line: " + str(line_number))
                sys.exit(0)
        elif (char == "$"):
            commentComplete = False
            currentHashtag = currentHashtag + char
            while (char):
                if (char == "\n"):
                    line_counter = line_counter + 1
                elif (char == "#"):
                    char = inputfile.read(1)
                    if (char == "$"):
                        commentComplete = True
                        break
                else:
                    pass 
                char = inputfile.read(1)
            if (commentComplete == False): 
                print("Comments not closed, at line: " + str(line_number))
                sys.exit(0)
            else:
                tk = Token("comment","comment",line_number)
        else:
            print("Invalid use of '#', at line: " + str(line_number))
            sys.exit(0)
        return tk

    def isQuotation(self, char,line_number):
        current = char
        for k in range(9):
            char  = inputfile.read(1)
            current = current + char
        if (current == '"__main__"'):
            tk = Token(current,"keyword",line_number)
            return tk
        else:
            print("Invalid use of double quotation marks, at line: " + str(line_number))
            sys.exit(0)

    def isUnderscore(self, char,line_number):
        currentWord = char
        for v in range(7):
            char  = inputfile.read(1)
            currentWord = currentWord + char
        if (currentWord == "__name__"):
            tk = Token(currentWord,"keyword",line_number)
            return tk
        else:
            print("Invalid use of '_', at line: " + str(line_number))
            sys.exit(0)

# --- Intermediate Code --- #
class Intermediate:
    def __init__(self) -> None:
        pass

    def genQuad(self, operator, operand1, operand2, operand3):
        global quadID
        global quadList
        quad = [quadID, operator, operand1, operand2, operand3]
        quadID = quadID + 1
        quadList.append(quad)
        return quad
    
    def nextQuad(self):
        global quadID
        return (quadID)
        
    def newTemp(self):
        global TempCounter
        variab = "T_" + str(TempCounter)
        TempCounter += 1
        return(variab)

    def emptyList(self):
        emptyList = []
        return emptyList
        
    def makeList(self, label):
        makeList = [label]
        return makeList
        
    def mergeList(self, list1, list2):
        newList = list1 + list2
        return (newList)
        
    def backPatch(self, list, label):
        global quadList
        for i in range(len(quadList)):
            if (quadList[i][0] in list):
                quadList[i][4] = label

# --- Symbol Table -------- #
class Entity:
    def __init__(self, name):
        self.name = name

class Variable(Entity):
    def __init__(self, name, datatype, offset):
        super().__init__(name)
        self.datatype = datatype
        self.offset = offset

    def printEntity(self):
        print("Name: " + self.name + " / Data Type: " + self.datatype + " / Offset: " + str(self.offset))

    def toString(self):
        return ("Name: " + self.name + " / Data Type: " + self.datatype + " / Offset: " + str(self.offset))

class FormalParameter(Entity):
    def __init__(self, name, datatype, mode):
        super().__init__(name)
        self.datatype = datatype
        self.mode = mode

    def printEntity(self):
        print("Name: " + self.name + " / Data Type: " + self.datatype + " / Mode: " + self.mode)

    def toString(self):
        return ("Name: " + self.name + " / Data Type: " + self.datatype + " / Mode: " + self.mode)

class TemporaryVariable(Variable):
    def __init__(self, name, datatype, offset):
        super().__init__(name, datatype, offset)

    def printEntity(self):
        print("Name: " + self.name + " / Data Type: " + self.datatype + " / Offset: " + str(self.offset))

    def toString(self):
        return ("Name: " + self.name + " / Data Type: " + self.datatype + " / Offset: " + str(self.offset))

class Function(Entity):
    def __init__(self, name, datatype, startingQuad, framelength, formalParameters):
        super().__init__(name)
        self.datatype = datatype
        self.startingQuad = startingQuad
        self.framelength = framelength
        self.formalParameters = formalParameters

    def printEntity(self):
        print("Name: " + self.name + " / Data Type: " + self.datatype + " / Starting Quad: " + str(self.startingQuad) + " / Frame Length: " + str(self.framelength)+ " / Formal Parameters: " + str(self.formalParameters))

    def toString(self):
        return ("Name: " + self.name + " / Data Type: " + self.datatype + " / Starting Quad: " + str(self.startingQuad) + " / Frame Length: " + str(self.framelength)+ " / Formal Parameters: " + str(self.formalParameters))

    def changeStartingQuad(self,number):
        self.startingQuad = number

    def changeFrameLength(self,number):
        self.framelength = number

class Parameter(FormalParameter):
    def __init__(self, name, datatype, mode, offset):
        super().__init__(name, datatype, mode)
        self.offset = offset

    def printEntity(self):
        print("Name: " + self.name + " / Data Type: " + self.datatype + " / Mode: " + self.mode + " / Offset: " + str(self.offset))

    def toString(self):
        return ("Name: " + self.name + " / Data Type: " + self.datatype + " / Mode: " + self.mode + " / Offset: " + str(self.offset))
        
class Scope:
    def __init__(self, name):
        self.name = name
        self.scopeEntities = []
        
    def addEntity(self, entity):
        self.scopeEntities.append(entity)
        pass
    
    def getEntity(self, name):
        for entity in self.scopeEntities:
            if (entity.name == name):
                return entity
        
class Table:
    def __init__(self) -> None:
        self.symTab = []

    def addScope(self,name):
        x = Scope(name)
        self.symTab.append(x)

    def removeScope(self):
        self.symTab = self.symTab[0:-1]

    def findInTable(self,name):
        res = 10
        for i in range(len(self.symTab)):
            p = - (i+1)
            for j in range(len(self.symTab[p].scopeEntities)):
                if (self.symTab[p].scopeEntities[j].name == name):
                    res = p
                else:
                    pass
        if (res == 10):
            print("Did not find entity in symbol table" + name)
            sys.exit(0)
        else:
            return res
            
# --- Syntax Analyzer ----- #
class Syntax:
    def __init__(self) -> None:
        pass
    
    def getCurrentToken(self,lista):
        global pointer
        if (pointer >= (len(lista))):
            temp = Token("END OF TOKENS","END OF TOKENS",0)
        else:
            temp = lista[pointer]
            pointer = pointer+1 
        return temp
    
    def errorGen(self, errorTypeIdentifier):
        global token
        errorRegister = {
            "id": "ERROR: A valid identifier was expected at line: ",
            "addOp": "ERROR: A \"+\" or \"-\" was expected at line: ",
            "mulOp": "ERROR: A \"*\" or \"//\" was expected at line: ",
            "assign": "ERROR: The \"=\" was expected at line: ",
            "relOp": "ERROR: Valid relational operator symbol (<, >, !=, <=, >=, ==) is expected at line: ",
            "closeBraces": "ERROR: Braces \"#}\" are not closed at line: ",
            "openBraces": "ERROR: Brace \"#{\" expected at line: ",
            "closeBracket": "ERROR: Brackets are not closed at line: ",
            "openBracket": "ERROR: Bracket expected at line: ",
            "closePar": "ERROR: Parentheses are not closed at line: ",
            "openPar": "ERROR: Parenthese expected at line: ",
            "eof": "ERROR: Characters found after \"#}\", line: ",
            "colon": "ERROR: A \":\" was expected at line: ",
            "semicolon": "ERROR: A \";\" was expected at line: ",
            "comma": "ERROR: A \",\" was expected at line: ",
            "defName": "ERROR: Invalid function name at line: ",
            "def": "ERROR: \"def\" keyword was expected at line: ",
            "declare": "ERROR: \"#declare\" keyword was expected at line: ",
            "int": "ERROR: \"int\" keyword was expected at line: ",
            "input": "ERROR: \"input\" keyword was expected at line: ",
            "print": "ERROR: \"print\" keyword was expected at line: ",
            "while": "ERROR: \"while\" keyword was expected at line: ",
            "if": "ERROR: \"if\" keyword was expected at line: ",
            "else": "ERROR: \"else\" keyword was expected at line: ",
            "name": "ERROR: \"__name__\" keyword was expected at line: ",
            "main": "ERROR: " "__main__" " keyword was expected at line: "
        }
        print(errorRegister[errorTypeIdentifier] + str(token.line_number))
        sys.exit(0) 

    def startRule(self, lista):
        global token
        token = self.getCurrentToken(lista)
        self.def_main_part(lista)
        self.call_main_part(lista)

    def def_main_part(self, lista):
        global token
        symbolic.addScope("Program")
        self.def_main_function(lista)
        while (token.recognized_string == "def"):
            self.def_main_function(lista)
        return
    
    def def_main_function(self, lista):
        global token
        global Offset
        global framelength 
        Offset = 12
        if (token.recognized_string == "def"):
            token = self.getCurrentToken(lista)
            if (token.family == "identifier"):
                ent = Function(token.recognized_string, "int", 0, 0, 0)
                symbolic.symTab[-1].addEntity(ent)
                mainFunctionName = token.recognized_string
                symbolic.addScope(mainFunctionName)
                token = self.getCurrentToken(lista)
                if (token.recognized_string == "("):
                    token = self.getCurrentToken(lista)
                    if (token.recognized_string == ")"):
                        token = self.getCurrentToken(lista)
                        if (token.recognized_string == ":"):
                            token = self.getCurrentToken(lista)
                            if (token.recognized_string == "#{"):
                                token = self.getCurrentToken(lista)
                                self.declarations(lista)
                                rememberOffset = Offset
                                while (token.recognized_string == "def"):
                                    self.def_function(lista)
                                Offset = rememberOffset
                                inter.genQuad("begin_block", mainFunctionName, "_", "_")
                                startQuad = inter.nextQuad()
                                symbolic.symTab[-2].scopeEntities[-1].changeStartingQuad(startQuad)
                                self.statements(lista)
                                endQuad = inter.nextQuad()
                                inter.genQuad("end_block", mainFunctionName, "_", "_")
                                symbolic.symTab[-2].scopeEntities[-1].changeFrameLength(Offset)
                                begin = startQuad - 1
                                end = endQuad + 1
                                framelength = Offset 
                                fin.finalCodeGen(begin,end)
                                exp.printSymbolTable()
                                exp.exportSymbolTable()
                                symbolic.removeScope()
                                if (token.recognized_string == "#}"):
                                    token = self.getCurrentToken(lista)
                                    return
                                else:
                                    self.errorGen("closeBraces")
                            else:
                                self.errorGen("openBraces")
                        else:
                            self.errorGen("colon")
                    else:
                        self.errorGen("closePar")
                else:
                    self.errorGen("openPar")
            else:
                self.errorGen("id")
        else:
            self.errorGen("def")

    def def_function(self, lista):
        global token
        global Offset
        if (token.recognized_string == "def"):
            token = self.getCurrentToken(lista)
            if (token.family == "identifier"):
                ent = Function(token.recognized_string, "int", 0, 0, 0)
                symbolic.symTab[-1].addEntity(ent)
                functionName = token.recognized_string
                symbolic.addScope(functionName)
                Offset = 12
                token = self.getCurrentToken(lista)
                if (token.recognized_string == "("):
                    token = self.getCurrentToken(lista)
                    self.id_list(lista,"param")
                    if (token.recognized_string == ")"):
                        token = self.getCurrentToken(lista)
                        if (token.recognized_string == ":"):
                            token = self.getCurrentToken(lista)
                            if (token.recognized_string == "#{"):
                                token = self.getCurrentToken(lista)
                                self.declarations(lista)
                                rememberOffset = Offset
                                while (token.recognized_string == "def"):
                                    self.def_function(lista)
                                Offset = rememberOffset
                                inter.genQuad("begin_block", functionName, "_", "_")
                                startQuad = inter.nextQuad()
                                symbolic.symTab[-2].scopeEntities[-1].changeStartingQuad(startQuad)
                                self.statements(lista)
                                endQuad = inter.nextQuad()
                                inter.genQuad("end_block", functionName, "_", "_")
                                symbolic.symTab[-2].scopeEntities[-1].changeFrameLength(Offset)
                                begin = startQuad - 1
                                end = endQuad + 1
                                fin.finalCodeGen(begin,end)
                                exp.printSymbolTable()
                                exp.exportSymbolTable()
                                symbolic.removeScope()
                                if (token.recognized_string == "#}"):
                                    token = self.getCurrentToken(lista)
                                    return
                                else:
                                    self.errorGen("closeBraces")
                            else:
                                self.errorGen("openBraces")
                        else:
                            self.errorGen("colon")
                    else:
                        self.errorGen("closePar")
                else:
                    self.errorGen("openPar")
            else:
                self.errorGen("id")
        else:
            self.errorGen("def")

    def declarations(self, lista):
        global token
        while (token.recognized_string == "#declare"):
            self.declaration_line(lista)
        return
            
    def declaration_line(self, lista):
        global token
        if (token.recognized_string == "#declare"):
            token = self.getCurrentToken(lista)
            self.id_list(lista,"declare")
            return
        else:
            self.errorGen("declare")
           
    def statements(self, lista):
        global token
        if ((token.recognized_string == "if") or (token.recognized_string == "while") or (token.recognized_string == "print") or (token.recognized_string == "return") or (token.family == "identifier")):
            self.statement(lista)
            while ((token.recognized_string == "if") or (token.recognized_string == "while") or (token.recognized_string == "print") or (token.recognized_string == "return") or (token.family == "identifier")):
                self.statement(lista)
            return
        else:
            print("Missing statement at line:" + str(token.line_number))
            sys.exit(0)

    def statement(self, lista):
        global token
        if ((token.recognized_string == "if") or (token.recognized_string == "while")):
            self.structured_statement(lista)
        else:
            self.simple_statement(lista)
        return

    def structured_statement(self, lista):
        global token
        if (token.recognized_string == "if"):
            self.if_stat(lista)
        elif (token.recognized_string == "while"):
            self.while_stat(lista)
        else:
            print("Something went wrong at structured statement at line: " + str(token.line_number))
            sys.exit(0)
        return

    def simple_statement(self, lista):
        global token
        if (token.recognized_string == "print"):
            self.print_stat(lista)
        elif (token.recognized_string == "return"):
            self.return_stat(lista)
        elif (token.family == "identifier"):
            self.assignment_stat(lista)
        else:
            print("Something went wrong at simple statement at line: " + str(token.line_number))
            sys.exit(0)    
        return

    def assignment_stat(self, lista):
        global token
        if (token.family == "identifier"):
            sourcePlace = token.recognized_string
            token = self.getCurrentToken(lista)
            if (token.recognized_string == "="):
                token = self.getCurrentToken(lista)
                if (token.recognized_string == "int"):
                    token = self.getCurrentToken(lista)
                    if (token.recognized_string == "("):
                        token = self.getCurrentToken(lista)
                        if (token.recognized_string == "input"):
                            token = self.getCurrentToken(lista)
                            if (token.recognized_string == "("):
                                token = self.getCurrentToken(lista)
                                if (token.recognized_string == ")"):
                                    token = self.getCurrentToken(lista)
                                    if (token.recognized_string == ")"):
                                        token = self.getCurrentToken(lista)
                                        if (token.recognized_string == ";"):
                                            token = self.getCurrentToken(lista)
                                            inter.genQuad("in", sourcePlace, "_", "_")  
                                            return
                                        else:
                                            self.errorGen("semicolon")
                                    else:
                                        self.errorGen("closePar")
                                else:
                                    self.errorGen("closePar")
                            else:
                                self.errorGen("openPar")
                        else:
                            self.errorGen("input")
                    else:
                        self.errorGen("openPar")
                else:
                    expPlace = self.expression(lista)
                    if (token.recognized_string == ";"):
                        token = self.getCurrentToken(lista)
                        inter.genQuad("=", expPlace, "_", sourcePlace) 
                    else:
                        self.errorGen("semicolon")
            else:
                self.errorGen("assign")
        else:
            self.errorGen("id")

    def print_stat(self, lista):
        global token
        if (token.recognized_string == "print"):
            token = self.getCurrentToken(lista)
            if (token.recognized_string == "("):
                token = self.getCurrentToken(lista)
                exp = self.expression(lista)
                if (token.recognized_string == ")"):
                    token = self.getCurrentToken(lista)
                    if (token.recognized_string == ";"):
                        token = self.getCurrentToken(lista)
                        inter.genQuad("out", exp, "_", "_")
                        return
                    else:
                        self.errorGen("semicolon")
                else:
                    self.errorGen("closePar")
            else:
                self.errorGen("openPar")
        else:
            self.errorGen("print")

    def return_stat(self, lista):
        global token
        if (token.recognized_string == "return"):
            token = self.getCurrentToken(lista)
            if (token.recognized_string == "("):
                token = self.getCurrentToken(lista)
                exp = self.expression(lista)
                if (token.recognized_string == ")"):
                    token = self.getCurrentToken(lista)
                    if (token.recognized_string == ";"):
                        token = self.getCurrentToken(lista)
                        inter.genQuad("ret", exp, "_", "_")
                        return
                    else:
                        self.errorGen("semicolon")
                else:
                    self.errorGen("closePar")
            else:
                self.errorGen("openPar")
        else:
            self.errorGen("return")

    def if_stat(self, lista):
        global token
        if (token.recognized_string == "if"):
            token = self.getCurrentToken(lista)
            if (token.recognized_string == "("):
                token = self.getCurrentToken(lista)
                condPlace = self.condition(lista)
                if (token.recognized_string == ")"):
                    token = self.getCurrentToken(lista)
                    if (token.recognized_string == ":"):
                        token = self.getCurrentToken(lista)
                        if (token.recognized_string == "#{"):
                            token = self.getCurrentToken(lista)
                            inter.backPatch(condPlace[1],inter.nextQuad())
                            self.statements(lista)
                            ifList = inter.makeList(inter.nextQuad())
                            inter.genQuad("jump","_","_","_")
                            inter.backPatch(condPlace[0],inter.nextQuad())
                            if (token.recognized_string == "#}"):
                                token = self.getCurrentToken(lista)
                                if (token.recognized_string == "else"):
                                    token = self.getCurrentToken(lista)
                                    if (token.recognized_string == ":"):
                                        token = self.getCurrentToken(lista)
                                        if (token.recognized_string == "#{"):
                                            token = self.getCurrentToken(lista)
                                            self.statements(lista)
                                            if (token.recognized_string == "#}"):
                                                token = self.getCurrentToken(lista)
                                                inter.backPatch(ifList,inter.nextQuad())
                                                return
                                            else:
                                                self.errorGen("closeBraces")
                                        else:
                                            self.statement(lista)
                                            inter.backPatch(ifList,inter.nextQuad())
                                            return
                                    else:
                                        self.errorGen("colon")
                                else:
                                    inter.backPatch(ifList,inter.nextQuad())
                                    return
                            else:
                                self.errorGen("closeBraces")
                        else:
                            inter.backPatch(condPlace[1],inter.nextQuad())
                            self.statement(lista)
                            ifList = inter.makeList(inter.nextQuad())
                            inter.genQuad("jump","_","_","_")
                            inter.backPatch(condPlace[0],inter.nextQuad())
                            if (token.recognized_string == "else"):
                                token = self.getCurrentToken(lista)
                                if (token.recognized_string == ":"):
                                    token = self.getCurrentToken(lista)
                                    if (token.recognized_string == "#{"):
                                        token = self.getCurrentToken(lista)
                                        self.statements(lista)
                                        if (token.recognized_string == "#}"):
                                            token = self.getCurrentToken(lista)
                                            inter.backPatch(ifList,inter.nextQuad())
                                            return
                                        else:
                                            self.errorGen("closeBraces")
                                    else:
                                        self.statement(lista)
                                        inter.backPatch(ifList,inter.nextQuad())
                                        return
                                else:
                                    self.errorGen("colon")
                            else:
                                inter.backPatch(ifList,inter.nextQuad())
                                return                      
                    else:
                        self.errorGen("colon")
                else:
                    self.errorGen("closePar")
            else:
                self.errorGen("openPar")
        else:
            self.errorGen("if")

    def while_stat(self, lista):
        global token
        if (token.recognized_string == "while"):
            token = self.getCurrentToken(lista)
            conditionQuad = inter.nextQuad()
            if (token.recognized_string == "("):
                token = self.getCurrentToken(lista)
                conditionTemp = self.condition(lista)
                if (token.recognized_string == ")"):
                    token = self.getCurrentToken(lista)
                    if (token.recognized_string == ":"):
                        token = self.getCurrentToken(lista)
                        if (token.recognized_string == "#{"):
                            token = self.getCurrentToken(lista)
                            inter.backPatch(conditionTemp[1], inter.nextQuad())
                            self.statements(lista)
                            inter.genQuad("jump","_","_",conditionQuad)
                            inter.backPatch(conditionTemp[0], inter.nextQuad())
                            if (token.recognized_string == "#}"):
                                token = self.getCurrentToken(lista)
                                return 
                            else:
                                self.errorGen("closeBraces")
                        else:
                            inter.backPatch(conditionTemp[1], inter.nextQuad())
                            self.statement(lista)
                            inter.genQuad("jump","_","_",conditionQuad)
                            inter.backPatch(conditionTemp[0], inter.nextQuad())
                    else:
                        self.errorGen("colon")
                else:
                    self.errorGen("closePar")
            else:
                self.errorGen("openPar")
        else:
            self.errorGen("while")

    def id_list(self, lista, type):
        global token
        global Offset
        if (token.family == "identifier"):
            if (type == "declare"):
                ent = Variable(token.recognized_string, "int", Offset)
                Offset = Offset + 4
            else:
                ent = Parameter(token.recognized_string, "int", "cv", Offset)
                Offset = Offset + 4
                formPars = []
                formPars.append(ent.name)
            symbolic.symTab[-1].addEntity(ent)
            token = self.getCurrentToken(lista)
            while (token.recognized_string == ","):
                token = self.getCurrentToken(lista)
                if (token.family == "identifier"):
                    if (type == "declare"):
                        ent = Variable(token.recognized_string, "int", Offset)
                        Offset = Offset + 4
                    else:
                        ent = Parameter(token.recognized_string, "int", "cv", Offset)
                        Offset = Offset + 4
                        formPars.append(ent.name)
                    symbolic.symTab[-1].addEntity(ent)
                    token = self.getCurrentToken(lista)
                else:
                    self.errorGen("id")
            if (type == "param"):
                symbolic.symTab[-2].scopeEntities[-1].formalParameters = formPars
        else:
            pass
        return
    
    def expression(self, lista):
        global token
        global Offset
        term1Place = self.optional_sign(lista)
        r1 = self.term(lista)
        term1Place = term1Place + r1
        while (token.family == "addOperator"):
            op = token.recognized_string
            token = self.getCurrentToken(lista)
            term2Place = self.term(lista)
            w = inter.newTemp()
            inter.genQuad(op,term1Place,term2Place,w)
            term1Place = w
            ent = TemporaryVariable(w, "int", Offset)
            Offset = Offset + 4
            symbolic.symTab[-1].addEntity(ent)
        return term1Place

    def term(self, lista):
        global token
        global Offset
        factor1Place = self.factor(lista)
        while (token.family == "mulOperator"):
            op = token.recognized_string
            token = self.getCurrentToken(lista)
            factor2Place = self.factor(lista)
            w = inter.newTemp()
            inter.genQuad(op,factor1Place,factor2Place,w)
            factor1Place = w
            ent = TemporaryVariable(w, "int", Offset)
            Offset = Offset + 4
            symbolic.symTab[-1].addEntity(ent)
        return factor1Place

    def factor(self,lista):
        global token
        if (token.family == "number"):
            numPlace = token.recognized_string
            token = self.getCurrentToken(lista)
            return numPlace
        elif (token.recognized_string == "("):
            token = self.getCurrentToken(lista)
            expPlace = self.expression(lista)
            if (token.recognized_string == ")"):
                token = self.getCurrentToken(lista)
                return expPlace
            else:
                self.errorGen("closePar")
        elif (token.family == "identifier"):
            idPlace = token.recognized_string
            token = self.getCurrentToken(lista)
            idPlace2 = self.idtail(lista)
            if (idPlace2 == ""):
                return idPlace
            else:
                inter.genQuad("par",idPlace2,"ret","_")
                inter.genQuad("call",idPlace,"_","_")
                return idPlace2
        else:
            print("problem at factor at line:" + str(token.line_number))
            sys.exit(0)
            
    def idtail(self, lista):
        global token
        global Offset
        if (token.recognized_string == "("):
            token = self.getCurrentToken(lista)
            self.actual_par_list(lista)
            if (token.recognized_string == ")"):
                token = self.getCurrentToken(lista)
                newT = inter.newTemp()
                ent = Parameter(newT, "int", "ret", Offset)
                Offset = Offset + 4
                symbolic.symTab[-1].addEntity(ent)
                return newT
            else:
                self.errorGen("closePar")
        else:
            temp = ""
            return temp
        
    def actual_par_list(self, lista):
        global token
        if (token.recognized_string == ")"):
            return
        else:
            actParLiPlace = self.expression(lista)
            inter.genQuad("par",actParLiPlace,"cv","_")
            while (token.recognized_string == ","):
                token = self.getCurrentToken(lista)
                actParLiPlace = self.expression(lista)
                inter.genQuad("par",actParLiPlace,"cv","_")
            return
        
    def optional_sign(self, lista):
        global token
        optSignPlace = ""
        if (token.family == "addOperator"):
            optSignPlace = token.recognized_string
            token = self.getCurrentToken(lista)
        return optSignPlace

    def condition(self, lista):
        global token
        boolTerm = self.bool_term(lista)
        conditionTerm = boolTerm
        while (token.recognized_string == "or"):
                token = self.getCurrentToken(lista)
                inter.backPatch(conditionTerm[0],inter.nextQuad())
                boolTerm2 = self.bool_term(lista)
                conditionTerm[1] = inter.mergeList(conditionTerm[1],boolTerm2[1])
                conditionTerm[0] = boolTerm2[0]
        return conditionTerm

    def bool_term(self, lista):
        global token
        boolFactor = self.bool_factor(lista)
        boolTerm = boolFactor
        while (token.recognized_string == "and"):
                token = self.getCurrentToken(lista)
                inter.backPatch(boolTerm[1],inter.nextQuad())
                boolFactor2 = self.bool_factor(lista)
                boolTerm[0] = inter.mergeList(boolTerm[0],boolFactor2[0])
                boolTerm[1] = boolFactor2[1]
        return boolTerm
    
    def bool_factor(self, lista):
        global token 
        if (token.recognized_string == "not"):
            token = self.getCurrentToken(lista)
            if (token.recognized_string == "["):
                token = self.getCurrentToken(lista)
                b = self.condition(lista)
                if (token.recognized_string == "]"):
                    token = self.getCurrentToken(lista)
                    boolFactor = ["f","t"]
                    boolFactor[1] = b[0]
                    boolFactor[0] = b[1]
                    return boolFactor
                else:
                    self.errorGen("closeBracket")
            else:
                self.errorGen("openBracket")
        elif (token.recognized_string == "["):
            token = self.getCurrentToken(lista)
            b = self.condition(lista)
            if (token.recognized_string == "]"):
                token = self.getCurrentToken(lista)
                boolFactor = b
                return boolFactor
            else:
                self.errorGen("closeBracket")
        else:
            e1 = self.expression(lista)
            if (token.family == "relOperator"):
                op = token.recognized_string
                token = self.getCurrentToken(lista)
                e2 = self.expression(lista)
                boolFactor = ["f","t"]
                boolFactor[1] = inter.makeList(inter.nextQuad())
                inter.genQuad(op,e1,e2,"_")
                boolFactor[0] = inter.makeList(inter.nextQuad())
                inter.genQuad("jump","_","_","_")
                return boolFactor
            else:
                self.errorGen("relOp")

    def call_main_part(self, lista):
        global token
        if (token.recognized_string == "if"):
            token = self.getCurrentToken(lista)
            if (token.recognized_string == "__name__"):
                token = self.getCurrentToken(lista)
                if (token.recognized_string == "=="):
                    token = self.getCurrentToken(lista)
                    if (token.recognized_string == '"__main__"'):
                        token = self.getCurrentToken(lista)
                        if (token.recognized_string == ":"):
                            token = self.getCurrentToken(lista)
                            inter.genQuad("begin_block", "main", "_", "_")
                            startQuad = inter.nextQuad()
                            self.main_function_call(lista)
                            while (token.family == "identifier"):
                                self.main_function_call(lista)
                            inter.genQuad("halt", "_", "_", "_")
                            endQuad = inter.nextQuad()
                            inter.genQuad("end_block", "main", "_", "_")
                            begin = startQuad - 1
                            end = endQuad + 1
                            fin.finalCodeGen(begin,end)
                        else:
                            self.errorGen("colon")
                    else:
                        self.errorGen("main")
                else:
                    self.errorGen("relOp")
            else:
                self.errorGen("name")
        else:
            self.errorGen("if")

    def main_function_call(self, lista):
        global token
        if (token.family == "identifier"):
            mainFunctionName = token.recognized_string
            inter.genQuad("call", mainFunctionName, "_", "_")
            token = self.getCurrentToken(lista)
            if (token.recognized_string == "("):
                token = self.getCurrentToken(lista)
                if (token.recognized_string == ")"):
                    token = self.getCurrentToken(lista)
                    if (token.recognized_string == ";"):
                       token = self.getCurrentToken(lista)
                       return 
                    else:
                        self.errorGen("semiColon")
                else:
                    self.errorGen("closePar")
            else:
                self.errorGen("openPar")
        else:
            self.errorGen("id")

# --- Final Code ---------- #
class Final:
    def __init__(self) -> None:
        pass
    
    def produceFinal(self, line):
        global fclist
        fcline = line
        fclist.append(fcline)
        return 
    
    def gnlvcode(self,name):
        levels = symbolic.findInTable(name)
        en = symbolic.symTab[levels].getEntity(name)
        levels = -levels
        if (levels > 1):
            self.produceFinal("lw t0, -4(sp)")
            levels = levels-1
            for i in range(levels):
                self.produceFinal("lw t0, -4(t0)")
            self.produceFinal("addi t0, t0, -" + str(en.offset))
        else:
            pass
    
    def loadvr(self, name, register):
        if (name.isnumeric()):  
            self.produceFinal("li " + register + " , "+ name)
            return
        
        self.produceFinal("lw " + register + ", " + str(symbolic.findInTable(name)*4) + "(sp)")
        return
        #if (symbolic.findInTable(name) == -1):
        #    self.produceFinal("lw " + register + ", " + str(symbolic.findInTable(name)) + "(sp)")
        #else:
        #    self.gnlvcode(name)
        #    self.produceFinal("lw " + register + ", (t0)")        
        
    def storerv(self, register, name):
        self.produceFinal("sw " + register + ", " + str(symbolic.findInTable(name)*4) + "(sp)")
        return
        #if (symbolic.findInTable(name) == -1):
        #    self.produceFinal("sw " + register + ", " + str(symbolic.findInTable(name)) + "(sp)")
        #else:
        #    self.produceFinal("mv t4, " + register)
        #    self.gnlvcode(name)
        #    self.produceFinal("sw t4, ("+ register +")")
    
    def finalCodeLineGen(self,line):
        global i
        i = 1
        global framelength
        operator = line[1]
        operand1 = line[2]
        operand2 = line[3]
        operand3 = line[4]
        
        if (operator == "begin_block"):
            if (operand1 == "main"):
                self.produceFinal("main:\n")
                self.produceFinal("addi sp, sp, 12")
                self.produceFinal("mv gp, sp")
            else:
                self.produceFinal(operand1 + ":\n")
                self.produceFinal("sw ra, -0(sp)")
        elif (operator == "jump"):
            self.produceFinal("j " + "L" + str(operand3))				
        elif(operator == "end_block"): 
            if (operand1 == "main"): 
                return
            else:
                self.produceFinal("lw ra, (sp)")
                self.produceFinal("jr ra")
        elif (operator == "="):
            self.loadvr(operand1, "t0")
            self.storerv("t0", str(operand3))
        elif (operator == "+"):
            self.loadvr(operand1, "t1")
            self.loadvr(operand2, "t2")
            self.produceFinal("add t1, t1, t2")
            self.storerv("t1", str(operand3))
        elif (operator == "-"):
            self.loadvr(operand1, "t1")
            self.loadvr(operand2, "t2")
            self.produceFinal("sub t1, t1, t2")
            self.storerv("t1", str(operand3))
        elif (operator == "*"):
            self.loadvr(operand1, "t1")
            self.loadvr(operand2, "t2")
            self.produceFinal("mul t1, t1, t2")
            self.storerv("t1", str(operand3))
        elif (operator == "//"):
            self.loadvr(operand1, "t1")
            self.loadvr(operand2, "t2")
            self.produceFinal("div t1, t1, t2")
            self.storerv("t1", str(operand3))
        elif (operator == ">"):
            self.loadvr(operand1, "t1")
            self.loadvr(operand2, "t2")
            self.produceFinal("bgt t1, t2, L" + str(operand3))
        elif (operator == "<"):
            self.loadvr(operand1, "t1")
            self.loadvr(operand2, "t2")
            self.produceFinal("blt t1, t2, L" + str(operand3))
        elif (operator == ">="):
            self.loadvr(operand1, "t1")
            self.loadvr(operand2, "t2")
            self.produceFinal("bge t1, t2, L" + str(operand3))
        elif (operator == "<="):
            self.loadvr(operand1, "t1")
            self.loadvr(operand2, "t2")
            self.produceFinal("ble t1, t2, L" + str(operand3))
        elif (operator == "=="):
            self.loadvr(operand1, "t1")
            self.loadvr(operand2, "t2")
            self.produceFinal("beq t1, t2, L" + str(operand3))
        elif (operator == "!="):
            self.loadvr(operand1, "t1")
            self.loadvr(operand2, "t2")
            self.produceFinal("bne t1, t2, L" + str(operand3))
        elif (operator == "out"):
            self.loadvr(operand1, "a0")
            self.produceFinal("li a7, 1")
            self.produceFinal("ecall")
            self.produceFinal("la a0, str_nl")
            self.produceFinal("li a7, 4")
            self.produceFinal("ecall")
        elif (operator == "in"):
            self.produceFinal("li a7, 5")
            self.produceFinal("ecall")
            self.storerv("a0", str(operand1))
        elif (operator == "ret"): 
            self.loadvr(operand1, "t1")
            self.produceFinal("lw t0, -8(sp)")
            self.produceFinal("sw t1, (t0)")
            self.produceFinal("lw ra, (sp)")
            self.produceFinal("jr ra")
        elif (operator =="par"): 
            if (i == 1):
                self.produceFinal("addi fp, sp, " + str(framelength))
            n = 12+4*(i-1)
            if (operand2 == "cv"): 
                self.loadvr(operand1, "t0")
                self.produceFinal("sw t0, -" + str(n) + "(fp)")
            elif (operand2 == "ret"): 
                #lvl = symbolic.findInTable(operand1) 
                #ent = symbolic.symTab[lvl].getEntity(operand1)
                #print(lvl)
                #self.produceFinal("addi t0, sp, -" + str(ent.offset)) 
                self.produceFinal("sw t0, -8(fp)")
            else: 
                print("ERROR: parameter name is not valid: " + str(operand1)) 
            i += 1
        elif (operator == "call"): 
            i = 1
                
            if (operand1[:5] == "main_"): 
                self.produceFinal("addi fp, sp, " + str(framelength))
                self.produceFinal("sw sp, -4(fp)")
                self.produceFinal("addi sp, sp, " + str(framelength))
                self.produceFinal("jal " + str(operand1))
                self.produceFinal("addi sp, sp, -" + str(framelength))
                return
            self.produceFinal("addi sp, sp, " + str(framelength))
            self.produceFinal("jal " + str(operand1))
            self.produceFinal("addi sp, sp, -" + str(framelength))
        elif (operator == "halt"):
            self.produceFinal("li a0, 0")
            self.produceFinal("li a7, 93")
            self.produceFinal("ecall")
        else:
            print("ERROR: Operator is not valid: " + operator)
            
    def finalCodeGen(self, begin, end):
        global quadList
        for i in range(begin,end):
            self.produceFinal("L" + str(quadList[i][0]) + ":        ")  
            self.produceFinal("        ")  
            self.finalCodeLineGen(quadList[i])
            self.produceFinal("        ")  

# function to get the current Token
def get_tklist():
    lex=Lex()
    x = inputfile.read(1)
    global line_counter
    line_counter = 1
    tkl = []
    while(x):
        if ((x == " ") or (x == "\t")):
            pass
        elif (x == "\n"):
            line_counter = line_counter + 1
        elif (x.isnumeric()):
            tkl.append(lex.isNumber(x,line_counter))
        elif (x.isalpha()):
            tkl.append(lex.isLetter(x,line_counter))
        elif (x == "_"):
            tkl.append(lex.isUnderscore(x,line_counter))
        elif (x == '"'):
            tkl.append(lex.isQuotation(x,line_counter))    
        elif (x == "+" or x == "-"):
            tkl.append(lex.isAddOperator(x,line_counter))
        elif (x == "*" or x == "/"):
            tkl.append(lex.isMulOperator(x,line_counter))
        elif (x == "<" or x == ">" or x == "!"):
            tkl.append(lex.isRelOp(x,line_counter))
        elif (x == "="):
            tkl.append(lex.isAssign(x,line_counter))
        elif (x == ";" or x == "," or x == ":"):
            tkl.append(lex.isDelimeter(x,line_counter))
        elif (x == "(" or x == ")" or x == "[" or x == "]"):
            tkl.append(lex.isGroupSymbol(x,line_counter))
        elif (x == "#"):
            temp = lex.isHashtag(x,line_counter)
            if (temp.family == "comment"):
                pass
            else:
                tkl.append(temp)
        else:
            print("Invalid character: " + x + " at line: " + str(line_counter))
            sys.exit(0)
        x = inputfile.read(1)
    return tkl 

# --- Prints & Exports ---- #
class Export:
    def __init__(self) -> None:
        pass
    
    # prints each token with its family and line number in terminal
    def printLex(self, tokenlist):
        for h in range(len(tokenlist)):
            print(tokenlist[h].recognized_string + "        family: " + tokenlist[h].family + " ,    line:  " + str(tokenlist[h].line_number))

    # exports tokens in text form to .lex file
    def exportLex(self, tokenlist):
        with open(lexi, 'w') as outputLex:
            outputLex.write("# Christos Seretis | 4486 | cse84486 | cs04486@uoi.gr\n# Dimitrios Tsiapalis | 4511 | cse84511 | cs04511@uoi.gr\n\n# Lex Tokens\n\n")
            for items in tokenlist:
                outputLex.write("%s\n" % items)

    # prints intermediate code in terminal
    def printIntermediate(self):
        for h in range(len(quadList)):
            print(quadList[h])
            
    # exports intermediate code in text form to .int file
    def exportIntermediate(self):
        with open(intermed, 'w') as outputInter:
            outputInter.write("# Christos Seretis | 4486 | cse84486 | cs04486@uoi.gr\n# Dimitrios Tsiapalis | 4511 | cse84511 | cs04511@uoi.gr\n\n# Intermediate Code\n\n")
            for items in quadList:
                outputInter.write("%s\n" % items)
    
    # prints symbol code in terminal
    def printSymbolTable(self):
        print("***************** SYMBOL TABLE ********************")
        for h in range(len(symbolic.symTab)):
            print("-------- LEVEL: " + symbolic.symTab[h].name + " ---------")
            for j in range(len(symbolic.symTab[h].scopeEntities)):
                symbolic.symTab[h].scopeEntities[j].printEntity()
        print("**************** END           ********************")
            
    # exports intermediate code in text form to .symbt file            
    def exportSymbolTable(self):
        x = "***************** SYMBOL TABLE ********************"
        y = "**************** END           ********************"
        with open(symbtab, 'a') as outputSymbt:
            outputSymbt.write("%s\n" % x)
            outputSymbt.write("\n")
            for thing in range(len(symbolic.symTab)):
                z = "-------- LEVEL: " + symbolic.symTab[thing].name + " ---------"
                outputSymbt.write("%s\n" % z)
                for thing2 in range(len(symbolic.symTab[thing].scopeEntities)):
                    outputSymbt.write("%s\n" % symbolic.symTab[thing].scopeEntities[thing2].toString())
            outputSymbt.write("\n")
            outputSymbt.write("%s\n" % y)
            outputSymbt.write("\n")
            outputSymbt.write("\n")
            outputSymbt.close()
            
    # prints final code in RISC-V Assembly to .asm file
    def printFinal(self):
        for h in range(len(fclist)):
            print(fclist[h])
            
    # exports final code in RISC-V Assembly to .asm file
    def exportFinal(self):
        with open(finalAsm, 'w') as outputAsm:
            outputAsm.write("# Christos Seretis | 4486 | cse84486 | cs04486@uoi.gr\n# Dimitrios Tsiapalis | 4511 | cse84511 | cs04511@uoi.gr\n\n# RISC-V Assembly Code Generated by cutePy Compiler\n\n")
            outputAsm.write(".data\nstr_nl: .asciz \"\\n\"\n.text\n\n")
            outputAsm.write("L999:\n\nj main\n\n")
            for items in fclist:
                outputAsm.write("%s\n" % items)
        
# --- Main function ------- #
if (__name__ == "__main__"):
    #inputfile = open('maintest.cpy', 'r')
    inputfile = open(sys.argv[1], 'r')
    #lexi = "maintest.lex"
    infile = sys.argv[1]
    lexi = infile[:-4] + ".lex"
    #intermed = "maintest.int"
    intermed = infile[:-4] + ".int"
    #symbtab = "maintest.symbt"
    symbtab = infile[:-4] + ".symbt"
    #finalAsm = "maintest.asm"
    finalAsm = infile[:-4] + ".asm"
    
    pointer = 0
    quadID = 0
    TempCounter = 1
    quadList = []
    fclist = []
    
    exp = Export()
    syntax = Syntax()
    inter = Intermediate()
    symbolic = Table()
    fin = Final()
    
    result = get_tklist()
    #exp.printLex(result)
    exp.exportLex(result)
    print("*** Tokens for Lex generated! ***")
    syntax.startRule(result)
    print("*** Syntax is correct! ***")
    exp.printIntermediate()
    exp.exportIntermediate()
    print("*** Intermediate Code Generated! ***")
    exp.printSymbolTable()
    exp.exportSymbolTable()
    print("*** Symbol Table Generated! ***")
    #exp.printFinal()
    exp.exportFinal()
    print("*** Final Code in RISC-V Assembly Generated! ***")
    inputfile.close()
    print("*** cutePy Compilation completed succesfully! ***")
    sys.exit(0)
