import pygame
from network import Network
import threading

pygame.init()

win_res = [640, 640]

clock = pygame.time.Clock()

pygame.display.set_caption('chess')

display = pygame.display.set_mode(win_res)
screen = pygame.Surface((160, 160))

# Dictionary to map piece characters to their respective image files
piece_images = {
    'R': pygame.image.load('data/images/w_rook.png'),
    'N': pygame.image.load('data/images/w_knight.png'),
    'B': pygame.image.load('data/images/w_bishop.png'),
    'Q': pygame.image.load('data/images/w_queen.png'),
    'K': pygame.image.load('data/images/w_king.png'),
    'P': pygame.image.load('data/images/w_pawn.png'),
    'r': pygame.image.load('data/images/b_rook.png'),
    'n': pygame.image.load('data/images/b_knight.png'),
    'b': pygame.image.load('data/images/b_bishop.png'),
    'q': pygame.image.load('data/images/b_queen.png'),
    'k': pygame.image.load('data/images/b_king.png'),
    'p': pygame.image.load('data/images/b_pawn.png')
}

received_move_str = None


def receive_thread(net, turn_var):
    global received_move_str

    while True:
        try:
            data = net.receive()
            if data is not None:
                # Process received data here as needed
                # Update turn variable if data is received
                turn_var[0] = 'black' if turn_var[0] == 'white' else 'white'

                received_move_str = data
        except Exception as e:
            print("Error receiving data:", e)
            break


def draw_board(valid_moves=None):
    for rows in range(8):
        for cols in range(8):
            if (rows + cols) % 2 == 0:
                pygame.draw.rect(screen, (255, 220, 200), [20 * rows, 20 * cols, 20, 20])
            else:
                pygame.draw.rect(screen, (200, 100, 75), [20 * rows, 20 * cols, 20, 20])

    if valid_moves:
        # Create a surface with per-pixel alpha
        transparent_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        transparent_surface.fill((255, 0, 0, 128))  # Red with semi-transparent alpha value (128)

        for move in valid_moves:
            row, col = move
            # Blit the transparent surface onto the screen
            screen.blit(transparent_surface, (20 * col, 20 * row))


def draw_pieces(board):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece is not None and piece != ' ':
                piece_image = piece_images[piece]
                # Calculate the coordinates to center the piece in the square
                x = col * 20 + (20 - piece_image.get_width()) // 2
                y = row * 20 + (20 - piece_image.get_height()) // 2
                screen.blit(piece_image, (x, y))


def get_row_col(p):
    x, y = p
    row = y // 80
    col = x // 80
    return row, col


def get_e_attacked_squares(turn, board):
        attacked_squares = []

        # Define the enemy color based on the current turn
        enemy_color = 'black' if turn == 'white' else 'white'

        # Iterate over each square on the board
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece is not None:
                    if piece != ' ' and piece.islower() == (enemy_color == 'black') and piece is not None:
                        # Check if this piece can attack the square (row, col)
                        for r in range(8):
                            for c in range(8):
                                # Exclude pawn forward moves
                                if piece.lower() != 'p' or (row - r) * (-1 if enemy_color == 'black' else 1) != 1:
                                    if is_valid_move((row, col), (r, c), piece, enemy_color, board):
                                        attacked_squares.append((r, c))
                                # Include pawn diagonal moves
                                elif abs(col - c) == 1 and abs(row - r) == 1:
                                    if is_valid_move((row, col), (r, c), piece, enemy_color, board):
                                        attacked_squares.append((r, c))

        return attacked_squares


def is_under_check(turn, e_attacked_squares, board):
    for square in e_attacked_squares:
        row, col = square
        if turn == 'white':
            if board[row][col] == 'K':
                return True

        elif turn == 'black':
            if board[row][col] == 'k':
                return True

    return False


def is_future_proof(turn, board, start, end, piece):
    if piece is not None:
        test_board = [row[:] for row in board]
        s_row, s_col = start
        e_row, e_col = end
        test_board[s_row][s_col] = ' '
        test_board[e_row][e_col] = piece

        attacked_squares = get_e_attacked_squares(turn, test_board)

        if is_under_check(turn, attacked_squares, test_board):
            return False
        else:
            return True


def is_valid_move(start, end, s_piece, turn, board):
    if s_piece is not None:
        s_row, s_col = start
        e_row, e_col = end

        if start == end:
            return False


        if (turn == 'white' and not s_piece.isupper()) or (turn == 'black' and not s_piece.islower()):
            return False

        #pawn
        if s_piece.lower() == 'p':
            # Normal pawn move: one square forward
            if (turn == 'white' and e_row == s_row - 1) or (turn == 'black' and e_row == s_row + 1):
                if e_col == s_col and board[e_row][e_col] == ' ':
                    return True

                elif abs(e_col - s_col) == 1 and ((board[e_row][e_col].islower() and turn == 'white') or (
                        board[e_row][e_col].isupper() and turn == 'black')):
                    return True

            # Initial pawn move: two squares forward from starting position
            elif (turn == 'white' and e_row == s_row - 2 and s_row == 6) or (
                    turn == 'black' and e_row == s_row + 2 and s_row == 1):
                if e_col == s_col and board[e_row][e_col] == ' ':
                    # Check if there are no pieces between the start and end positions
                    if all(board[r][s_col] == ' ' for r in range(s_row + 1, e_row)):
                        return True

        # Rook
        if s_piece.lower() == 'r':
            if (e_col == s_col) or (e_row == s_row):
                # Check if there are no pieces between the start and end positions
                if e_row == s_row:  # Horizontal move
                    if e_col > s_col:
                        if all(board[s_row][col] == ' ' for col in range(s_col + 1, e_col)):
                            if (turn == 'white' and not board[e_row][e_col].isupper()) or (
                                    turn == 'black' and not board[e_row][e_col].islower()):
                                return True
                    else:
                        if all(board[s_row][col] == ' ' for col in range(e_col + 1, s_col)):
                            if (turn == 'white' and not board[e_row][e_col].isupper()) or (
                                    turn == 'black' and not board[e_row][e_col].islower()):
                                return True
                else:  # Vertical move
                    if e_row > s_row:
                        if all(board[row][s_col] == ' ' for row in range(s_row + 1, e_row)):
                            if (turn == 'white' and not board[e_row][e_col].isupper()) or (
                                    turn == 'black' and not board[e_row][e_col].islower()):
                                return True
                    else:
                        if all(board[row][s_col] == ' ' for row in range(e_row + 1, s_row)):
                            if (turn == 'white' and not board[e_row][e_col].isupper()) or (
                                    turn == 'black' and not board[e_row][e_col].islower()):
                                return True

        # Bishop
        if s_piece.lower() == 'b':
            if abs(e_col - s_col) == abs(e_row - s_row) and ((turn == 'white' and not board[e_row][e_col].isupper()) or (
                    turn == 'black' and not board[e_row][e_col].islower())):
                # Check if there are no pieces between the start and end positions
                row_direction = 1 if e_row > s_row else -1
                col_direction = 1 if e_col > s_col else -1
                row, col = s_row + row_direction, s_col + col_direction
                while row != e_row and col != e_col:
                    if board[row][col] != ' ':
                        return False  # There's a piece blocking the bishop's path
                    row += row_direction
                    col += col_direction
                return True

        #queen
        if s_piece.lower() == 'q':
            if abs(e_col - s_col) == abs(e_row - s_row) and ((turn == 'white' and not board[e_row][e_col].isupper()) or (
                    turn == 'black' and not board[e_row][e_col].islower())):
                # Check if there are no pieces between the start and end positions
                row_direction = 1 if e_row > s_row else -1
                col_direction = 1 if e_col > s_col else -1
                row, col = s_row + row_direction, s_col + col_direction
                while row != e_row and col != e_col:
                    if board[row][col] != ' ':
                        return False  # There's a piece blocking the bishop's path
                    row += row_direction
                    col += col_direction
                return True

            elif (e_col == s_col) or (e_row == s_row):
                # Check if there are no pieces between the start and end positions
                if e_row == s_row:  # Horizontal move
                    if e_col > s_col:
                        if all(board[s_row][col] == ' ' for col in range(s_col + 1, e_col)):
                            if (turn == 'white' and not board[e_row][e_col].isupper()) or (
                                    turn == 'black' and not board[e_row][e_col].islower()):
                                return True

                    else:
                        if all(board[s_row][col] == ' ' for col in range(e_col + 1, s_col)):
                            if (turn == 'white' and not board[e_row][e_col].isupper()) or (
                                    turn == 'black' and not board[e_row][e_col].islower()):
                                return True

                else:  # Vertical move
                    if e_row > s_row:
                        if all(board[row][s_col] == ' ' for row in range(s_row + 1, e_row)):
                            if (turn == 'white' and not board[e_row][e_col].isupper()) or (
                                    turn == 'black' and not board[e_row][e_col].islower()):
                                return True

                    else:
                        if all(board[row][s_col] == ' ' for row in range(e_row + 1, s_row)):
                            if (turn == 'white' and not board[e_row][e_col].isupper()) or (
                                    turn == 'black' and not board[e_row][e_col].islower()):
                                return True

        #knight
        if s_piece.lower() == 'n':
            if ((abs(e_row - s_row) == 2 and abs(e_col - s_col) == 1) or (
                    abs(e_row - s_row) == 1 and abs(e_col - s_col) == 2)) and (
                    turn == 'white' and not board[e_row][e_col].isupper()):
                return True
            elif ((abs(e_row - s_row) == 2 and abs(e_col - s_col) == 1) or (
                    abs(e_row - s_row) == 1 and abs(e_col - s_col) == 2)) and (
                    turn == 'black' and not board[e_row][e_col].islower()):
                return True

        #king
        if s_piece.lower() == 'k':
            if abs(e_col - s_col) == 1 and (e_row == s_row or e_row - 1 == s_row or e_row + 1 == s_row):
                if (turn == 'white' and not board[e_row][e_col].isupper()) or (
                        turn == 'black' and not board[e_row][e_col].islower()):
                    return True
            elif abs(e_row - s_row) == 1 and (e_col == s_col or e_col - 1 == s_col or e_col + 1 == s_col):
                if (turn == 'white' and not board[e_row][e_col].isupper()) or (
                        turn == 'black' and not board[e_row][e_col].islower()):
                    return True


def can_castle_kingside(turn, board, kingside_moved, rook_moved):
    # Check if the king and rook are in their initial positions for kingside castling
    if turn == 'white':
        if board[7][4] == 'K' and board[7][7] == 'R' and not kingside_moved and not rook_moved:
            # Check if the squares between the king and rook are empty
            if all(board[7][col] == ' ' for col in range(5, 7)):
                return True
    else:
        if board[0][4] == 'k' and board[0][7] == 'r' and not kingside_moved and not rook_moved:
            # Check if the squares between the king and rook are empty
            if all(board[0][col] == ' ' for col in range(5, 7)):
                return True
    return False


def can_castle_queenside(turn, board, queenside_moved, rook_moved):
    # Check if the king and rook are in their initial positions for queenside castling
    if turn == 'white':
        if board[7][4] == 'K' and board[7][0] == 'R' and not queenside_moved and not rook_moved:
            # Check if the squares between the king and rook are empty
            if all(board[7][col] == ' ' for col in range(1, 4)):
                return True
    else:
        if board[0][4] == 'k' and board[0][0] == 'r' and not queenside_moved and not rook_moved:
            # Check if the squares between the king and rook are empty
            if all(board[0][col] == ' ' for col in range(1, 4)):
                return True
    return False


def castle_kingside(turn, board):
    if turn == 'white':
        board[7][6] = 'K'
        board[7][5] = 'R'
        board[7][4] = ' '
        board[7][7] = ' '
    else:
        board[0][6] = 'k'
        board[0][5] = 'r'
        board[0][4] = ' '
        board[0][7] = ' '


def castle_queenside(turn, board):
    if turn == 'white':
        board[7][2] = 'K'
        board[7][3] = 'R'
        board[7][4] = ' '
        board[7][0] = ' '
    else:
        board[0][2] = 'k'
        board[0][3] = 'r'
        board[0][4] = ' '
        board[0][0] = ' '


def get_all_possible_moves(turn, board):
    possible_moves = []

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if (turn == 'white' and piece.isupper()) or (turn == 'black' and piece.islower()):
                for r in range(8):
                    for c in range(8):
                        if is_valid_move((row, col), (r, c), piece, turn, board) and is_future_proof(turn, board,
                                                                                                     (row, col), (r, c),
                                                                                                     piece):
                            possible_moves.append(((row, col), (r, c), piece))

    return possible_moves


def parse_string_to_list(string):
    result = []
    current_pair = []
    num_buffer = ''
    for char in string:
        if char.isdigit():
            num_buffer += char
        elif char == ',':
            if num_buffer:
                current_pair.append(int(num_buffer))
                num_buffer = ''
        elif char == '[':
            current_pair = []
        elif char == ']':
            if num_buffer:
                current_pair.append(int(num_buffer))
                num_buffer = ''
            if current_pair:
                result.append(current_pair)
                current_pair = []
        else:
            if num_buffer:
                current_pair.append(int(num_buffer))
                num_buffer = ''
            if char != ' ' and char != "'":
                result.append(char)
    return result


def game_loop():

    global received_move_str
    n = Network("0.tcp.ap.ngrok.io")
    my_color = n.get_pos()

    # Example board configuration (you can replace this with your own logic)
    board = [
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    ]

    # Variables to track whether kingside and queenside castling are allowed
    white_kingside_moved = False
    white_queenside_moved = False
    black_kingside_moved = False
    black_queenside_moved = False

    # Variables to track whether the kings and rooks have moved
    white_king_moved = False
    black_king_moved = False

    selected_piece = None
    turn = ['white']

    valid_moves = []
    attacked_squares = []

    is_checkmate = False
    is_stalemate = False

    receive_thread_obj = threading.Thread(target=receive_thread, args=(n, turn))
    receive_thread_obj.daemon = True
    receive_thread_obj.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos1 = pygame.mouse.get_pos()
                    row1, col1 = get_row_col(pos1)
                    selected_piece = board[row1][col1]

                    if selected_piece != ' ':
                        valid_moves = []
                        for row in range(8):
                            for col in range(8):
                                if is_valid_move((row1, col1), (row, col), selected_piece, turn[0],
                                                 board) and is_future_proof(turn[0], board, (row1, col1), (row, col),
                                                                            selected_piece) and my_color == turn[0]:
                                    valid_moves.append([row, col])

                    else:
                        selected_piece = None  # Reset selected_piece to None when an empty square is clicked

            if event.type == pygame.MOUSEBUTTONUP:
                valid_moves = []
                if event.button == 1:
                    pos2 = pygame.mouse.get_pos()
                    row2, col2 = get_row_col(pos2)
                    if is_valid_move((row1, col1), (row2, col2), selected_piece, turn[0], board) and is_future_proof(turn[0],
                                                                                                                  board,
                                                                                                                  (row1,
                                                                                                                   col1),
                                                                                                                  (row2,
                                                                                                                   col2),
                                                                                                                  selected_piece) and my_color == turn[0]:
                        board[row2][col2] = selected_piece
                        board[row1][col1] = ' '
                        move = [[row2, col2], [row1, col1], selected_piece]
                        move_str = str(move)
                        n.send(move_str)

                        if selected_piece.lower() == 'k':
                            if turn[0] == 'white':
                                white_king_moved = True
                            else:
                                black_king_moved = True
                        turn[0] = 'black' if turn[0] == 'white' else 'white'
                        attacked_squares = get_e_attacked_squares(turn[0], board)
                        if is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0], board):
                            print('checkmate')
                            is_checkmate = True
                        elif not is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0],
                                                                                                              board):
                            print('stalemate')
                            is_stalemate = True
                        elif is_under_check(turn[0], attacked_squares, board):
                            print("check")

                    elif turn[0] == 'white':
                        if col2 == 6 and col1 == 4 and can_castle_kingside(turn[0], board, white_king_moved,
                                                                           white_kingside_moved) and row2 == 7 and row1 == 7:
                            castle_kingside(turn[0], board)
                            white_kingside_moved = True
                            white_king_moved = True
                            turn[0] = 'black'
                            attacked_squares = get_e_attacked_squares(turn[0], board)
                            if is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0],
                                                                                                            board):
                                print('checkmate')
                                is_checkmate = True
                            elif not is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0],
                                                                                                                  board):
                                print('stalemate')
                                is_stalemate = True
                            elif is_under_check(turn[0], attacked_squares, board):
                                print("check")

                            n.send("O-O")

                        elif col2 == 2 and col1 == 4 and can_castle_queenside(turn[0], board, white_king_moved,
                                                                              white_queenside_moved):
                            castle_queenside(turn[0], board)
                            white_queenside_moved = True
                            white_king_moved = True
                            turn = 'black'
                            attacked_squares = get_e_attacked_squares(turn[0], board)
                            if is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0],
                                                                                                            board):
                                print('checkmate')
                                is_checkmate = True
                            elif not is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0],
                                                                                                                  board):
                                print('stalemate')
                                is_stalemate = True
                            elif is_under_check(turn[0], attacked_squares, board):
                                print("check")

                            n.send("O-O-O")

                        else:
                            board[row1][col1] = selected_piece

                    elif turn[0] == 'black':
                        if col2 == 6 and col1 == 4 and can_castle_kingside(turn[0], board, black_king_moved,
                                                                           black_kingside_moved):
                            castle_kingside(turn[0], board)
                            black_kingside_moved = True
                            black_king_moved = True
                            turn[0] = 'white'
                            attacked_squares = get_e_attacked_squares(turn[0], board)
                            if is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0],
                                                                                                            board):
                                print('checkmate')
                                is_checkmate = True
                            elif not is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0],
                                                                                                                  board):
                                print('stalemate')
                                is_stalemate = True
                            elif is_under_check(turn[0], attacked_squares, board):
                                print("check")

                            n.send("O-O")

                        elif col2 == 2 and col1 == 4 and can_castle_queenside(turn[0], board, black_king_moved,
                                                                              black_queenside_moved):
                            castle_queenside(turn[0], board)
                            black_queenside_moved = True
                            black_king_moved = True
                            turn[0] = 'white'
                            attacked_squares = get_e_attacked_squares(turn[0], board)
                            if is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0],
                                                                                                            board):
                                print('checkmate')
                                is_checkmate = True
                            elif not is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0],
                                                                                                                  board):
                                print('stalemate')
                                is_stalemate = True
                            elif is_under_check(turn[0], attacked_squares, board):
                                print("check")

                            n.send("O-O-O")

                        else:
                            board[row1][col1] = selected_piece

        if my_color != turn and received_move_str is not None:

            # print(received_move_str)
            if received_move_str == "O-O":
                castle_kingside(turn, board)
                if turn == 'white':
                    white_king_moved = True
                elif turn == 'black':
                    black_king_moved = True

                attacked_squares = get_e_attacked_squares(turn[0], board)
                if is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0],
                                                                                                   board):
                    print('checkmate')
                    is_checkmate = True
                elif not is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0],
                                                                                                         board):
                    print('stalemate')
                    is_stalemate = True

            elif received_move_str == "O-O-O":
                castle_queenside(turn, board)
                if turn == 'white':
                    white_king_moved = True
                elif turn == 'black':
                    black_king_moved = True

                attacked_squares = get_e_attacked_squares(turn[0], board)
                if is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0],
                                                                                                   board):
                    print('checkmate')
                    is_checkmate = True
                elif not is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0],
                                                                                                         board):
                    print('stalemate')
                    is_stalemate = True

            else:
                received_move = parse_string_to_list(received_move_str)
                end = received_move[0]
                start = received_move[1]
                selected_piece = received_move[2]
                row1, col1 = start
                row2, col2 = end
                board[row2][col2] = selected_piece
                board[row1][col1] = ' '
                received_move_str = None
                attacked_squares = get_e_attacked_squares(turn[0], board)
                if is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0],
                                                                                                   board):
                    print('checkmate')
                    is_checkmate = True
                elif not is_under_check(turn[0], attacked_squares, board) and not get_all_possible_moves(turn[0],
                                                                                                         board):
                    print('stalemate')
                    is_stalemate = True

        draw_board(valid_moves)

        draw_pieces(board)

        if is_checkmate or is_stalemate:
            game_over(turn[0], is_checkmate, is_stalemate)

        else:
            # Scale the screen surface to match the display size
            scaled_screen = pygame.transform.scale(screen, (win_res[0], win_res[1]))

            # Blit the scaled screen onto the display
            display.blit(scaled_screen, (0, 0))

        pygame.display.update()
        clock.tick(60)

    pygame.quit()


def game_over(turn, is_checkmate, is_stalemate):
    # Create a font object
    font = pygame.font.Font(None, 36)

    winner = 'white' if turn == 'black' else 'black'

    if is_checkmate:
        # Create text surface for game over message
        game_over_text = "Game Over - Checkmate!"
        winner_text = winner.capitalize() + " won!"
        game_over_surface = font.render(game_over_text, True, (255, 255, 255))
        winner_surface = font.render(winner_text, True, (255, 255, 255))

        game_over_rect = game_over_surface.get_rect(center=(win_res[0] // 2, win_res[1] // 2 - 20))
        winner_rect = winner_surface.get_rect(center=(win_res[0] // 2, win_res[1] // 2 + 20))

        # Draw a semi-transparent rectangle as background for the message
        pygame.draw.rect(display, (0, 0, 0, 200), (100, 100, win_res[0] - 200, win_res[1] - 200))

        # Blit the text onto the display
        display.blit(game_over_surface, game_over_rect)
        display.blit(winner_surface, winner_rect)

    elif is_stalemate:
        # Create text surface for game over message
        game_over_text = "Game Over - stalemate!"
        winner_text = "It was a draw!"
        game_over_surface = font.render(game_over_text, True, (255, 255, 255))
        winner_surface = font.render(winner_text, True, (255, 255, 255))

        game_over_rect = game_over_surface.get_rect(center=(win_res[0] // 2, win_res[1] // 2 - 20))
        winner_rect = winner_surface.get_rect(center=(win_res[0] // 2, win_res[1] // 2 + 20))

        # Draw a semi-transparent rectangle as background for the message
        pygame.draw.rect(display, (0, 0, 0, 200), (100, 100, win_res[0] - 200, win_res[1] - 200))

        # Blit the text onto the display
        display.blit(game_over_surface, game_over_rect)
        display.blit(winner_surface, winner_rect)

    # Update the display
    pygame.display.update()


game_loop()
