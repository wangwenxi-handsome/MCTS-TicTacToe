from mcts import Board, MCTS


class TicTacToe:
    # 人类为'o', ai为'*', 未落子为'0'
    def __init__(self, person_first=False):
        self.first = person_first
        self.board = Board([['0' for i in range(3)] for j in range(3)])
    
    def person_step(self, ):
        while(1):
            inputs = input("you are 'o' and please input position like 0,2: ").split(",")
            try:
                x = int(inputs[0])
                y = int(inputs[1])
                success = self.board.step(x, y, 'o')
                if success:
                    break
                else:
                    print("input is not valid")
            except:
                print("input is not valid")
            
    
    def check_game_over(self, ):
        tag = self.board.done()
        if tag == 0:
            return False
        if tag == 1:
            print("tie")
            return True
        if tag == 2:
            print("you win")
            return True
        if tag == 3:
            print("you lose")
            return True
    
    def run(self, ):
        if self.first:
            self.person_step()

        while(1):
            mcts = MCTS(self.board)
            mcts.run()
            x, y = mcts.opt_step()
            self.board.step(x, y, '*')
            self.board.render()
            if self.check_game_over():
                break 
            self.person_step()
            if self.check_game_over():
                self.board.render()
                break 


if __name__ == "__main__":
    game = TicTacToe(person_first=False)
    game.run()