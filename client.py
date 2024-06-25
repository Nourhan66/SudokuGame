#client.py

from tkinter import *
from threading import *
from socket import *
from tkinter import messagebox
from tkinter import ttk
import pickle

player = 1


def check(row,col):
    #check rows
    for i in range(len(board[0])):
        if int(board[row][i]) == int(board[row][col]) and i != col:
            return False

    #check col
    for i in range(len(board[0])):
        if int(board[i][col]) == int(board[row][col]) and i != row:
            return False

    #check box
    box_x = col // 3  #(0,1,2)
    box_y = row // 3

    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if int(board[i][j]) == int(board[row][col]) and i != row and j != col:
                return False

    return True

def on_click(row, col):
   global score
   global player
   if player == 1 :
       if board[row][col] == 0:  # If the cell is empty
        entry = Entry(window,fg='blue', width=4, justify="center")
        entry.grid(row=row, column=col)
        entry.focus_set()  # Set focus to the entry widget
        entry.bind("<Return>", lambda event, r=row, c=col: update_board(event, r, c))  # Bind return key press event
        player=2
        
def update_board(event, row, col):
    global score
    global player
    value = event.widget.get()  # Get the value entered by the user

    value = int(value)  # Convert the value to an integer
    if 1 <= value <= 9:  # Ensure the entered value is in the valid range
        board[row][col] = value  # Update the board with the entered value
        ch =  check(row,col)
        if ch == True:
            score= score + 1
            #send play
            data= (row , col ,value,score)
            # Serialize the data
            data = pickle.dumps(data)
            # Send the serialized data to the client
            client_socket.send(data)

            score_label.config(text="Score: " + str(score))  # Update score label
            event.widget.config(state="readonly")  # Disable the entry widget
        else:
            # If the entered number violates Sudoku rules, reset the cell
            board[row][col] = 0
            event.widget.delete(0, END)  # Clear the entry widget
            messagebox.showerror("Invalid Input", "The entered number violates Sudoku rules.")
            label = Label(window, text=" ", bg='red',width=4, height=2, relief="solid")
            label.grid(row=row, column=col)
            player =2
            data = (row, col, 0,score)
            data = pickle.dumps(data)
            # Send the serialized data to the client
            client_socket.send(data)

    else:
     event.widget.delete(0, END)  # Clear the entry widget

def is_board_full():
    for row in board:
        for cell in row:
            if cell == 0:
                return False
    return True


def handle_play(row,col,val,score2):
    global player
    board[row][col]=val
    if val != 0:
        label = Label(window, text=str(board[row][col]),fg='red', width=4, height=2, relief="solid")
        label.grid(row=row, column=col)

        if (is_board_full()):
            if score > score2:
                messagebox.showinfo("Congratulations:- ", "player 1 ")
            elif score < score2:
                messagebox.showinfo("Congratulations:- ", "player 2")
            else:
                messagebox.showinfo("Congratulations:- ", "player 1 and player 2")
    player = 1


window = Tk()

window.title('Sudoku Player 1')
window.geometry('380x380')
board = [
        [7, 8, 0, 4, 0, 0, 1, 2, 0],
        [6, 0, 0, 0, 7, 5, 0, 0, 9],
        [0, 0, 0, 6, 0, 1, 0, 7, 8],
        [0, 0, 7, 0, 4, 0, 2, 6, 0],
        [0, 0, 1, 0, 5, 0, 9, 3, 0],
        [9, 0, 4, 0, 6, 0, 0, 0, 5],
        [0, 7, 0, 3, 0, 0, 0, 1, 2],
        [1, 2, 0, 0, 0, 7, 4, 0, 0],
        [0, 4, 9, 2, 0, 6, 0, 0, 7]
    ]

score = 0
score_label = Label(window,text='Score: 0' , width=6, height=2,bg='green',fg='black')
score_label.grid(row=30, column= 10, padx=10,pady=10)


for i in range(9):
    for j in range(9):
        if board[i][j] !=0:
            label = Label(window, text=str(board[i][j]),bg='red', width=4 , height=2, relief="solid")
            label.grid(row=i, column=j)
        else:
            label = Label(window, text=" ",bg='red', width=4, height=2, relief="solid")
            label.grid(row=i, column=j)
            label.bind("<Button-1>", lambda e, row=i, col=j: on_click(row, col))  # Bind left click event


client_socket = socket(AF_INET,SOCK_STREAM)
client_socket.connect(('127.0.0.1',49000))

def receive_msg():
    while True:
        data = client_socket.recv(1024)
        if data:
            row, col, value ,score= pickle.loads(data)

            handle_play(row, col, value,score)


thread = Thread(target=receive_msg)
thread.start()

mainloop()