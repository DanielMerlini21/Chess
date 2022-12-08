
"""
EXTRA:
get rid of edges!

Magic Bitboards
OBJECTIVE:
Create a ROOK hash table of all the indexes of relevant blockes when times by a value and shifted a number of bits for each [square][hash]

Step 1
find all the magic numbers (most effecient)

basic algorithm

function rook_moves(composite_board, square) {
  masked_composite = composite_board & rook_masks[square];
  hash_key = shitty_hash(masked_composite, square);
  return rook_table[square][hash_key];
}

function shitty_hash(masked_composite, square) {
  return (masked_composite * magics[square]) >> shifts[square];
}

func gen_magic_index(bitboard, magic_number):
    return (bitboard * magic_number) >> 54

func gen_magic_number(square):
    occupancy_combos[4096] = all possible occupancies on relevant squares
    attack_combos[4096] = attack mask for each occupancy above
    lookup_table[4096] = init with all zeros

    forever:
        magic_number = random 64-bit integer
        clear lookup_table
        for each occupancy in occupancy_combos
            let index = gen_magic_index(occupancy, magic_number)
            if lookup_table[index] == 0
                lookup_table[index] = attack_combos[occupancy]
            else if lookup_table[index] != attack_combos[occupancy]
                fail this iteration

    return magic_number

ROOK
sliding pieces once found including attack use XOR for own color.
using OR for other color (edges)

when finding magic
--> if overlaps when removing edges then remove edges that dont over lap. (rook)

"""
import itertools
import random
import math

magics = {} # [square]
shifts = {} # [square]
rook_table = {} # [square][hash_key]
attack_combos = {} # attack masks [occ]
lookup_table = {} # [hash_key]


piece_positions = ["R", "N", "B", "Q", "K", "B", "N", "R", # 56
                  "P", "P", "P", "P", "P", "P", "P", "P", # 49
                  " ", " ", " ", " ", " ", " ", " ", " ", # 42
                  " ", " ", " ", " ", " ", " ", " ", " ", # 35
                  "k", " ", " ", " ", " ", " ", " ", " ", # 28
                  " ", " ", " ", " ", " ", " ", " ", " ", # 21
                  "p", "p", "p", "p", "p", "p", "p", "p", # 14
                  "r", "n", "b", "q", "k", "b", "n", "r"] # 7

RANK = 2
FILE = 2
BINARY = RANK+FILE
SQUARES = FILE*RANK

# Functions
def generate_random_binary(length):
    all_random_binary = []
    start = 2**(length)
    for number in range(start):
        binary_number = "{:b}".format(number).zfill(length)
        all_random_binary.append(binary_number)
    return all_random_binary

def bitboards(chess_board, piece_name):
    # creates bitboards required
    # binary 1 2 4 8 16 32 64... (2)^n       
    # this makes it efficient because word sizes are 64 bit in 64 bit cpu wiki
    a, w, b, p, af, bf, gf, hf = (0,) * 8 # create bit board variables
    bitboards = {} # store all bitboards
    counter = 0
    length = len(chess_board) - 1 # because start from 0
    start = RANK - 1
    end = 0
    for index, tile in enumerate(chess_board):
        index = length - index # 63, 62, 61, 60... reverses order
        if index % RANK != start:
            af += 2**(index)
        if index % RANK != start - 1:
            bf += 2**(index)
        if index % RANK != end + 1:
            gf += 2**(index)
        if index % RANK != end:
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
    board = "{:b}".format(bitboard).zfill(SQUARES) # :Squares b used to remove b and into binary and makes it Squares bits long
    for rank in range(RANK): # 0100 => top: 01 bottom: 00
        for file in range(FILE):
            print(board[RANK*rank+file], end = " ")
        print()
    print()

def king_compute(piece, color, lookup_table):
    # binary shift : **2 moves right **1/2 moves left 1 space
    # rose compass
    king_clip_file_a = lookup_table[piece] & lookup_table["a file"]
    king_clip_file_h = lookup_table[piece] & lookup_table["h file"]
    print_bitboard(king_clip_file_h)
    spot_1 = king_clip_file_a << 1
    spot_2 = king_clip_file_h >> 1
    spot_3 = king_clip_file_h << RANK-1
    spot_4 = king_clip_file_a >> RANK-1
    spot_5 = lookup_table[piece] >> RANK
    spot_6 = lookup_table[piece] << RANK
    spot_7 = king_clip_file_h >> RANK+1
    spot_8 = king_clip_file_a << RANK+1
    king_moves = spot_1 | spot_2 | spot_3 | spot_4 | spot_5 | spot_6 | spot_7 | spot_8
    return king_moves & lookup_table[color]

def knight_compute(piece, color, lookup_table):
    clip_a = lookup_table[piece] & lookup_table["a file"]
    clip_a_b = lookup_table[piece] & lookup_table["a file"] & lookup_table["b file"]
    clip_h = lookup_table[piece] & lookup_table["h file"] 
    clip_g_h = lookup_table[piece] & lookup_table["h file"] & lookup_table["g file"]
    
    print_bitboard(lookup_table["b file"])
    print_bitboard(lookup_table["g file"])
    spot_1 = clip_a >> (RANK*2) - 1 
    spot_2 = clip_a_b >> (RANK) - 2
    spot_3 = clip_a_b << (RANK) + 2
    spot_4 = clip_a << (RANK * 2) + 1

    spot_5 = clip_h >> (RANK * 2) + 1
    spot_6 = clip_g_h >> (RANK) + 2
    spot_7 = clip_g_h << (RANK) - 2 
    spot_8 = clip_h  << (RANK*2) - 1

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

def generate_all_possible_combinations():
    # Constants
    all_combinations_total = {}
    for index in range(0, SQUARES): # SQUARES
        # Defining variables
        all_combinations_set = set()
        rank_of_index = index // RANK
        column_of_index = index % FILE
        combinations = generate_random_binary(BINARY)
        # Go though all combinations
        for comb in combinations:
            # Defining variables
            file = comb[0:FILE]
            rank = comb[FILE:SQUARES]
            bitboard_for_column = 0
            bitboard_for_row = 0
            # Rank created
            bitboard_for_row = int(file, 2)
            bitboard_for_row = bitboard_for_row << rank_of_index * FILE
            counter_for_column = 1
            # File created
            for i in range(0, SQUARES):
                if i % FILE == column_of_index:
                    if str(rank[-counter_for_column]) == "1":
                        bitboard_for_column += 2**(i)
                    counter_for_column += 1
            pos = 2**index
            total = bitboard_for_row | pos | bitboard_for_column
            all_combinations_set.add(total)
        all_combinations_total[str(index)] = all_combinations_set
    return all_combinations_total

def get_lsb_index(binary):
    binary = "{:b}".format(binary)
    for v, i in enumerate(binary:
        if v == "1":
            index = i
            break
    print(binary, index)
    return index

def sort_combinations(combinations):
    for index in range():
        for comb in combinations["0"]

def attack_combos_func(board, pos):
    # Constants
    orig_board = board
    file = pos % FILE
    rank =  pos // RANK
    # Variables
    new = 0
    """
    if nothing changes in the board when you "or"
    new shifted bit then it means there is something
    blocking it so it breaks.
    """
    # RANK RIGHT
    prev_board = None
    start = 2**pos # if pos is 0 start is 1 so no math.log error :)
    # print((math.log(start,2)), (math.log(start,2)) // RANK, rank, (math.log(start,2)) // RANK == rank, prev_board != board)
    while prev_board != board and (math.log(start,2)) // RANK == rank:
        new = new | start
        start = start >> 1 # because only when sure that its not at the end
        prev_board = board
        board = board | start
    # RANK LEFT
    prev_board = -0.1
    start = 2**pos
    while prev_board != board and (math.log(start,2)) // RANK == rank:
        new = new | start
        prev_board = board
        start = start << 1
        board = board | start  
    board = orig_board
    # FILE DOWN
    prev_board = -0.1
    start = 2**pos
    while prev_board != board and (math.log(start,2)) // RANK >= 0:
        new = new | start
        prev_board = board
        start = start >> RANK
        board = board | start
    # FILE UP
    prev_board = -0.1
    start = 2**pos
    while prev_board != board and (math.log(start,2)) // RANK <= 7:
        new = new | start
        prev_board = board
        start = start << RANK
        board = board | start
    start = 2**pos
    new = new | start
    return new

def create_empty_lookup():
    table = {}
    for i in range(80):
        table[str(i)] = "None"
    return table

#for i in range(0, 64):   
#    print(rook_attacks(i))


def gen_magic_index(bitboard, magic_number):
    return (bitboard * magic_number) >> 4

def get_binary(stringVal):
    binary = int(stringVal, 2)
    return binary
def gen_magic_number(start_index):
    magic_found = False
    occupancy_combos = generate_all_possible_combinations()
    lookup_table = create_empty_lookup()
    while True:
        if magic_found == True:
            break
        magic_found = True
        magic_number = random.getrandbits(SQUARES)
        lookup_table = create_empty_lookup()
        for occupancy in occupancy_combos[start_index]:
            print_bitboard(occupancy)
            ans = attack_combos_func(occupancy, int(start_index))
            index = gen_magic_index(occupancy, magic_number)
            if index not in lookup_table.keys():
                lookup_table[index] = ans
            elif lookup_table[index] != ans:
                magic_found = False
                break
    return magic_number, lookup_table

all_combinations = generate_all_possible_combinations()
#magic, lookup = gen_magic_number("0")
#binary = get_binary("1001")
#index = gen_magic_index(binary, magic)
#solution = lookup[index]
#print_bitboard(solution)




#print(attack_combos_func(2374687232445, 63))

#x = []
#for b in lst:
#    num = 0
#    for i in b:
#       num = 2 * num + i
#    x.append(num)



# where_piece_can_move(piece_positions, "n")
# where_piece_can_move(piece_positions, "K")



