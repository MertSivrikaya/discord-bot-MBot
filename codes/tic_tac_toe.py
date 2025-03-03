class GameManager():

    def __init__(self,p1_symbol = "x",p2_symbol = "o"):

        self.p1 = p1_symbol
        self.p2 = p2_symbol
        self.create_board()

    def create_board(self):
        
        self.board = [[0 for col in range(3)] for row in range(3)]  # 0 for blank spaces on the board
    
    def get_visualized_board(self):
        
        top = "_______"
        row1 = "|"
        row2 = "|"
        row3 = "|"

        for col in self.board[0]:
            if col == 0:
                row1 += "_"
            else:
                row1 += col

            row1+= "|"

        for col in self.board[1]:
            if col == 0:
                row2 += "_"
            else:
                row2 += col

            row2+= "|"
        
        for col in self.board[2]:
            if col == 0:
                row3 += "_"
            else:
                row3 += col

            row3+= "|"

        visualized_board = "\n".join([top,row1,row2,row3])
        return visualized_board

    def check_if_empty(self,row,column):

        return self.board[row][column] == 0

    def make_a_move(self,symbol,row,column):
        
        self.board[row][column] = symbol

    def check_game_end(self):
        
        winner_symbol= ""

        for row in self.board:  #row check
            if row[0] == row[1] and row[1] == row[2] and not row[0] == 0:
                winner_symbol = row[0]

        for col in range(3):   #column check
            if self.board[0][col] == self.board[1][col] and self.board[1][col] == self.board[2][col] and not self.board[0][col] == 0:
                winner_symbol = self.board[0][col]
                
        if self.board[0][0] == self.board[1][1] and self.board[1][1] == self.board[2][2] and not self.board[0][0] == 0:  #Diagonal check
            winner_symbol = self.board[0][0]

        if self.board[0][2] == self.board[1][1] and self.board[1][1] == self.board[2][0] and not self.board[0][2] == 0:  #Diagonal check
            winner_symbol = self.board[0][2]
                
        for i in [self.p1,self.p2]:
            if winner_symbol == i:
                return (True,winner_symbol)

        draw = True
        
        for row in self.board:
            if draw:
                for col in row:
                    if col == 0:
                        draw = False
                        break
            else:
                break
            

        if draw:
            return (True,"draw")

        return (False,winner_symbol)

        

#game_manager = GameManager()
#print(game_manager.get_visualized_board())

"""
 _ _ _
|_|_|x|
|_|_|_|
|o|_|_|
 
 
 """

