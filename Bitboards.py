piece_positions = ["R", "N", "B", "Q", "K", "B", "N", "R",
                  "P", "P", "P", "P", "P", "P", "P", "P",
                  " ", " ", " ", " ", " ", " ", " ", " ",
                  " ", " ", " ", " ", " ", " ", " ", " ",
                  "k", " ", " ", " ", " ", " ", " ", " ",
                  " ", " ", " ", " ", " ", " ", " ", " ",
                  "p", "p", "p", "p", "p", "p", "p", "p",
                  "r", "n", "b", "q", "k", "b", "n", "r"]
ROW = 8
FILE = 8

def bitboards(chess_board, piece_name):
    # creates bitboards required
    # binary 1 2 4 8 16 32 64... (2)^n       
    # this makes it efficient because word sizes are 64 bit in 64 bit cpu wiki
    a, w, b, p, af, bf, gf, hf = (0,) * 8 # create bit board variables
    bitboards = {} # store all bitboards
    counter = 0
    length = len(chess_board) - 1 # because start from 0
    start = ROW - 1
    end = 0
    for index, tile in enumerate(chess_board):
        index = length - index # 63, 62, 61, 60... reverses order
        # print(f"index {index} h file {index % ROW} tile {tile}")
        if index % ROW != start:
            af += 2**(index)
        if index % ROW != start - 1:
            bf += 2**(index)
        if index % ROW != end + 1:
            gf += 2**(index)
        if index % ROW != end:
            hf += 2**(index)
        if tile != " ":
            if tile == piece_name:
                p += 2**(index) # 1 where piece name
            if tile.islower() == True:
                w += 2**(index) # 1 where white piece
            else:
                b += 2**(index) # 1 where black piece
        else:
            a += 2**(index) # 1 where empty square

    
    # adding to dictionary
    bitboards["all pieces"] = a
    bitboards["white pieces"] = b | a # 0 on white
    bitboards["black pieces"] = w | a # 0 on black
    bitboards["a file"] = af
    bitboards["b file"] = bf
    bitboards["g file"] = gf
    bitboards["h file"] = hf
    bitboards[str(piece_name)] = p
    return bitboards

def print_bitboard(bitboard):
    # print(len(f"{bitboard:b}"))
    board = "{:b}".format(bitboard).zfill(64) # :064b used to remove b and into binary and makes it 64 bits long 
    # print(board)
    for i in range(8): # goes from rank 0 to 8 biggest first
        print(board[8*i+0] + " " + board[8*i+1] + " " + board[8*i+2] + " " + 
              board[8*i+3] + " " + board[8*i+4] + " " + board[8*i+5] + " " + 
              board[8*i+6] + " " + board[8*i+7])
    print("\n")

def king_compute(piece, color, lookup_table):
    # binary shift : **2 moves right **1/2 moves left 1 space
    # rose compass
    king_clip_file_a = lookup_table[piece] & lookup_table["a file"]
    king_clip_file_h = lookup_table[piece] & lookup_table["h file"]
    print_bitboard(king_clip_file_h)
    spot_1 = king_clip_file_a << 1
    spot_2 = king_clip_file_h >> 1
    spot_3 = king_clip_file_h << ROW-1
    spot_4 = king_clip_file_a >> ROW-1
    spot_5 = lookup_table[piece] >> ROW
    spot_6 = lookup_table[piece] << ROW
    spot_7 = king_clip_file_h >> ROW+1
    spot_8 = king_clip_file_a << ROW+1
    king_moves = spot_1 | spot_2 | spot_3 | spot_4 | spot_5 | spot_6 | spot_7 | spot_8
    return king_moves & lookup_table[color]

def knight_compute(piece, color, lookup_table):
    clip_a = lookup_table[piece] & lookup_table["a file"]
    clip_a_b = lookup_table[piece] & lookup_table["a file"] & lookup_table["b file"]
    clip_h = lookup_table[piece] & lookup_table["h file"] 
    clip_g_h = lookup_table[piece] & lookup_table["h file"] & lookup_table["g file"]
    
    print_bitboard(lookup_table["b file"])
    print_bitboard(lookup_table["g file"])
    spot_1 = clip_a >> (ROW*2) - 1 
    spot_2 = clip_a_b >> (ROW) - 2
    spot_3 = clip_a_b << (ROW) + 2
    spot_4 = clip_a << (ROW * 2) + 1

    spot_5 = clip_h >> (ROW * 2) + 1
    spot_6 = clip_g_h >> (ROW) + 2
    spot_7 = clip_g_h << (ROW) - 2 
    spot_8 = clip_h  << (ROW*2) - 1

    knight_moves = spot_1 | spot_2 | spot_3 | spot_4 | spot_5 | spot_6 | spot_7 | spot_8
    return knight_moves & lookup_table[color]

def where_piece_can_move(chess_board, piece_name):
    # check where piece can move
    bitboards_dict = bitboards(chess_board, piece_name) # returns all the bitboards required
    # goes through each piece
    if piece_name == "k":
        moves= king_compute("k", "white pieces", bitboards_dict)
    elif piece_name == "K":
        moves = king_compute("K","black pieces", bitboards_dict)
    elif piece_name == "n":
        moves = knight_compute("n", "white pieces", bitboards_dict)    
    elif piece_name == "N":
        moves = knight_compute("N", "Black pieces", bitboards_dict)
    print_bitboard(moves)
                            
where_piece_can_move(piece_positions, "n")
# where_piece_can_move(piece_positions, "K")
