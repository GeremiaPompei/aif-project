import gym
import minihack
from nle import nethack

import random
from random import randint
from functools import reduce
import numpy as np
import logging as lg


all_openings = {}
algorithm_steps = 0
hero_steps = 0
last_door_visit = 0
verbose = False

def print(*args):
    if verbose:
        lg.info(args)

# function to find cheracters position
def char_pos(obs, chars=['@']):
    return reduce(lambda x, y: x + y, [np.argwhere(obs['chars'] == ord(char)).tolist() for char in chars])


def char_surroundings(obs, fov_x=1, fov_y=1, char=''):
    pos = char_pos(obs, chars=[char])
    player_x = pos[0][0]
    player_y = pos[0][1]
    return char_surroundings_at_coors(obs, 1, 1, player_x, player_y)

def char_surroundings_at_coors(obs, fov_x=1, fov_y=1, player_x=0, player_y=0):
    if (player_x - fov_x < 0 or player_x + fov_x > len(obs['chars'])):
        fov_x = 1
    if (player_y - fov_y < 0 or player_y + fov_y > len(obs['chars'][0])):
        fov_y = 1

    fov = [["" for x in range(1 + fov_x * 2)] for y in range(1 + fov_y * 2)]
    a = 0
    c = 0
    for x in range(player_x - fov_x, player_x + fov_x + 1):
        for y in range(player_y - fov_y, player_y + fov_y + 1):
            fov[a][c] = chr(obs['chars'][x][y])
            c += 1
        c = 0
        a += 1

    return fov


def player_surroundings(obs, fov_x=1, fov_y=1, char='@'):
    return char_surroundings(obs, fov_x, fov_y, char)


def pick_key(env, obs):
    key_pos = char_pos(obs, '(')
    if key_pos == []:
        print("no key found")
        return False, env, obs
    else:
        print("key found")
        env, obs = reach_coordinates(env, obs, key_pos)
        print("key picked")
        return True, env, obs


def reach_coordinates(env, obs, to_reach):
    global hero_steps
    global algorithm_steps
    pos = char_pos(obs, chars=['@'])
    #print("in reach coordinates pos ", pos)
    player_x = pos[0][0]
    player_y = pos[0][1]

    #print(pos)
    if player_x != to_reach[0][0]:
        if player_x < to_reach[0][0]:
            stp = 2
        else:
            stp = 0

        while player_x != to_reach[0][0]:
            obs, reward, done, info = env.step(stp)
            print("step number: ", hero_steps)
            env.render()
            pos = char_pos(obs, chars=['@'])
            player_x, player_y = pos[0][0], pos[0][1]
            hero_steps += 1
            algorithm_steps +=1

        #print(pos)

    if player_y != to_reach[0][1]:
        if player_y < to_reach[0][1]:
            stp = 1
        else:
            stp = 3

        while player_y != to_reach[0][1]:
            obs, reward, done, info = env.step(stp)
            print("step number: ", hero_steps)
            env.render()
            pos = char_pos(obs, chars=['@'])
            player_x, player_y = pos[0][0], pos[0][1]
            hero_steps += 1
            algorithm_steps +=1

        print(pos)
    print("step number: ", hero_steps)
    env.render()
    return env, obs

def reach_stairs_down(observations, environment):
    stairs_pos = char_pos(observations, '>')
    print("stairs_pos ", stairs_pos)
    if stairs_pos != []:
        stairs_pos[0][1] -= 1
        environment, observations = reach_coordinates(environment, observations, stairs_pos)
        return True, environment, observations
    return False, environment, observations

def reach_stairs_up(observations, environment):
    stairs_pos = char_pos(observations, '<')
    if stairs_pos != []:
        stairs_pos[0][1] -= 1
        environment, observations = reach_coordinates(environment, observations, stairs_pos)
        return True, environment, observations
    return False, environment, observations


def get_lateral_direction(current_dir=0):
    rn = random.randint(-1, 1)
    print(rn)
    if rn < 0:
        rn = -1
    else:
        rn > 1

    if current_dir + rn > 3:
        current_dir = 3
    else:
        current_dir += rn

    return current_dir


def next_in_direction_char(observations, direction, char='#', check_laterals=False, to_check=[' ', ' ']):
    player_fov = char_surroundings(observations, char='@')
    if direction == 0:
        if player_fov[0][1] == char and check_laterals == False:
            return True
        elif player_fov[0][1] == char and check_laterals:
            if player_fov[0][0] == to_check[0] and player_fov[0][2] == to_check[1]:
                return True
    elif direction == 1:
        if player_fov[1][2] == char and check_laterals == False:
            return True
        elif player_fov[1][2] == char and check_laterals:
            if player_fov[1][0] == to_check[0] and player_fov[1][2] == to_check[1]:
                return True
    elif direction == 2:
        if player_fov[2][1] == char and check_laterals == False:
            return True
        elif player_fov[2][1] == char and check_laterals:
            if player_fov[2][0] == to_check[0] and player_fov[2][2] == to_check[1]:
                return True
    elif direction == 3:
        if player_fov[1][0] == char and check_laterals == False:
            return True
        elif player_fov[1][0] == char and check_laterals:
            if player_fov[1][0] == to_check[0] and player_fov[1][2] == to_check[0]:
                return True

    return False


def detect_impasse(observations, environment, direction):
    global algorithm_steps
    global hero_steps
    observations, reward, done, info = environment.step(direction)
    environment.render()
    hero_steps += 1
    algorithm_steps +=1

    if direction == 0 or direction == 2:
        if next_in_direction_char(observations, 1, char=' '):
            if next_in_direction_char(observations, 3, char=' '):
                if next_in_direction_char(observations, direction, char='|', check_laterals=True, to_check=[' ', ' ']) == False and next_in_direction_char(observations,direction, char='|', check_laterals=True,to_check=['-','-']) == False:
                    return True
    elif direction == 1 or direction == 3:
        if next_in_direction_char(observations, 0, char=' '):           
            if next_in_direction_char(observations, 2, char=' '):              
                if next_in_direction_char(observations, direction, char='-', check_laterals=True, to_check=[' ', ' ']) == False and next_in_direction_char(observations,direction, char='-',check_laterals=True,to_check=['|','|']) == False and next_in_direction_char(
                        observations, direction, char='-', check_laterals=True,to_check=['-', '|']) == False and next_in_direction_char(observations, direction, char='-',check_laterals=True,to_check=['|', '-']) == False:
                    return True
    return False


def is_opening_in_direction(observations, direction):
    if next_in_direction_char(observations, direction, '-', True, to_check=['|', '|']) or next_in_direction_char(
            observations, direction, '-', True, to_check=['-', '|']) or next_in_direction_char(observations, direction,'-', True, to_check=['|','-']) or next_in_direction_char(
            observations, direction, '-', True, to_check=[' ', ' ']):
        return True
    elif next_in_direction_char(observations, direction, '|', True, to_check=['-', '-']) or next_in_direction_char(
            observations, direction, '|', True, to_check=[' ', ' ']):
        return True
    elif next_in_direction_char(observations, direction, '.'):
        return True

    return False


def get_next_direction(direction, player_fov):
    if direction == 0 or direction == 2:
        if player_fov[1][0] == '#' and player_fov[1][2] == '#':
            return get_lateral_direction(direction)
        elif player_fov[1][0] != '#' and player_fov[1][0] != '+' and player_fov[1][0] != '.' and (
                (player_fov[1][0] != '-' and (player_fov[0][0] != '|' or player_fov[2][0] != '-')) or (
                (player_fov[1][2] != '-' and (player_fov[0][2] == ' ' and player_fov[2][2] == ' ')) or (
                player_fov[1][2] != '-' and (
                player_fov[0][2] == '|' and player_fov[2][2] == '|')))):  # add open doors based on char color
            return 1
        else:
            return 3
    else:
        if player_fov[0][1] == '#' and player_fov[2][1] == '#':
            return get_lateral_direction(direction)
        elif player_fov[0][1] != '#' and player_fov[0][1] != '+' and player_fov[0][1] != '.' and (
                (player_fov[0][1] != '|' and (player_fov[0][0] != '|' or player_fov[0][2] != '-')) or (
                player_fov[2][1] != '|' and player_fov[2][0] == ' ' and player_fov[2][2] == ' ') or (
                (player_fov[2][1] != '|' and (player_fov[2][0] == '-' or player_fov[2][2] == '-')))):
            return 2
        else:
            return 0


def navigate_corridor(observations, environment, direction, previous_position, random_movement=False, random_state=42):
    global algorithm_steps
    global hero_steps
    path_followed = []
    local_steps = 0
    message = ""
    while next_in_direction_char(observations, direction):# and local_steps < 15:
        observations, reward, done, info = environment.step(direction)
        algorithm_steps +=1
        hero_steps += 1

        if random_movement == True:
            print("Trying random")
            flag = random.randint(0, 100)
            initial_direction = direction
            if flag <= random_state:
                print("RANDOM CHANGE")
                previous_position = char_pos(observations)
                if (flag % 2) == 0:
                    direction += 1
                    if direction > 3:
                        direction = 0
                else:
                    direction -= 1
                    if direction < 0:
                        direction = 3
            observations, reward, done, info = environment.step(direction)
            algorithm_steps +=1
            hero_steps += 1

            if (previous_position == char_pos(observations)):
                direction = initial_direction
                print("useless change")
            else:
                print("useful change, from ", initial_direction, " to ", direction)
        
        previous_position = char_pos(observations)
        path_followed.append(direction)

        if next_in_direction_char(observations, direction) == False:
          break
        
    if is_opening_in_direction(observations, direction):
        observations, reward, done, info = environment.step(direction)
        path_followed.append(direction)
        environment.render()
        observations, reward, done, info = environment.step(direction)
        path_followed.append(direction)
        environment.render()

        final_check_before_next_iteration(observations, environment, direction)
        print("in room ")

        return path_followed, "room", direction, observations, environment
    elif detect_impasse(observations, environment, direction):
        print("impasse")
        print("direction ", direction)
        return path_followed, "impasse", direction, observations, environment
    else:
        print("change direction")
        player_fov = player_surroundings(observations)
        direction = get_next_direction(direction, player_fov)

        environment.render()
        new_path, message, direction, observations, environment = navigate_corridor(observations, environment, direction, previous_position)
        if type(new_path) != 'NoneType':
            path_followed.extend(new_path)

        return path_followed, message, direction, observations, environment


def get_all_openings(observaions, openings_sofar={}):
    doors = char_pos(observaions, chars=['+'])
    for door in doors:
        if str(door) not in openings_sofar:
            openings_sofar[str(door)] = 0

    doors_dash = char_pos(observaions, chars=['-'])
    for door_dash in doors_dash:
        x, y = door_dash

        if chr(observaions['chars'][x][y - 1]) == '.'  or chr(observaions['chars'][x][y - 1]) == '<'  or chr(observaions['chars'][x][y - 1]) == '>'  or chr(observaions['chars'][x][y - 1]) == '(':
            door_dash[0] = x
            door_dash[1] = y - 1 
            if str(door_dash) not in openings_sofar:
                openings_sofar[str(door_dash)] = 0            
        elif chr(observaions['chars'][x][y + 1]) == '.' or chr(observaions['chars'][x][y + 1]) == '<' or chr(observaions['chars'][x][y + 1]) == '>' or chr(observaions['chars'][x][y + 1]) == '(':
            door_dash[0] = x
            door_dash[1] = y + 1
            if str(door_dash) not in openings_sofar:
                openings_sofar[str(door_dash)] = 0
        
        if chr(observaions['chars'][x][y-1]) == ' ' and chr(observaions['chars'][x][y-2]) == '-':
            door_dash[0] = x
            door_dash[1] = y -1
            if str(door_dash) not in openings_sofar:
                openings_sofar[str(door_dash)] = 0
        elif chr(observaions['chars'][x][y+1]) == ' ' and chr(observaions['chars'][x][y+2]) == '-':
            door_dash[0] = x
            door_dash[1] = y +1
            if str(door_dash) not in openings_sofar:
                openings_sofar[str(door_dash)] = 0

    doors_pipe = char_pos(observaions, chars=['|'])
    for door_pipe in doors_pipe:
        x, y = door_pipe

        if chr(observaions['chars'][x - 1][y]) == '.' or chr(observaions['chars'][x - 1][y]) == '<'  or chr(observaions['chars'][x - 1][y]) == '>'  or chr(observaions['chars'][x - 1][y]) == '(':
            door_pipe[0] = x - 1
            door_pipe[1] = y
            if str(door_pipe) not in openings_sofar:
                openings_sofar[str(door_pipe)] = 0
        elif chr(observaions['chars'][x + 1][y]) == '.' or chr(observaions['chars'][x + 1][y]) == '<' or chr(observaions['chars'][x + 1][y]) == '>' or chr(observaions['chars'][x + 1][y]) == '(' :
            door_pipe[0] = x + 1
            door_pipe[1] = y
            if str(door_pipe) not in openings_sofar:
                openings_sofar[str(door_pipe)] = 0
        
        if chr(observaions['chars'][x-1][y]) == ' ' and (chr(observaions['chars'][x+2][y]) == '-' or chr(observaions['chars'][x+2][y]) == '|'):
            door_pipe[0] = x -1
            door_pipe[1] = y  
            if str(door_pipe) not in openings_sofar:
                openings_sofar[str(door_pipe)] = 0
        elif chr(observaions['chars'][x+1][y]) == ' ' and (chr(observaions['chars'][x-2][y]) == '-' or chr(observaions['chars'][x-2][y]) == '|'):
            door_pipe[0] = x +1
            door_pipe[1] = y 
            if str(door_pipe) not in openings_sofar:
                openings_sofar[str(door_pipe)] = 0

    to_sanitize = []
    for opening in openings_sofar:
        x, y = opening.strip('][').split(', ')
        # print("char ", observaions['chars'][int(x)][int(y)], " at ", x,y)
        if chr(observaions['chars'][int(x)][int(y)]) == ' ':
            # print("delated ")
            to_sanitize.append(str(opening))

    for delate in to_sanitize:
        del openings_sofar[delate]

    return openings_sofar


def get_closest_opening(all_known_openings, observations, not_explored=True, legal=True):
    # gets the closest door in respect to the player
    pos = char_pos(observations, chars=['@'])
    player_x, player_y = pos[0][0], pos[0][1]
    distance = 999999
    times_visited = 99999
    coord = [0, 0]
    for opening, explored in all_known_openings.items():
        if not_explored and explored == 0 or not_explored == False:
            x, y = opening.strip('][').split(', ')
            new_distance = ((int(x) - player_x) ** 2 + (int(y) - player_y) ** 2) ** 0.5
            if new_distance < distance and (legal == True and legal_opening(observations, [int(x), int(y)]) or legal == False) and explored < times_visited:
                distance = new_distance
                times_visited = explored
                coord[0] = int(x)
                coord[1] = int(y)
    return coord


def allign_to_opening(observations, environment, coords=[0,0]):
    global algorithm_steps
    global hero_steps
    door_surroundings = char_surroundings_at_coors(observations, 1,1,coords[0],coords[1])
    coord_to_reach = coords
    print("door_surroundings")
    print(door_surroundings[0])
    print(door_surroundings[1])
    print(door_surroundings[2])
    #this step is done in order to open the door and traverse it
    stp = 0

    if door_surroundings[0][1] == '.' or door_surroundings[0][1] == '@' or door_surroundings[0][1] == '<' or door_surroundings[0][1] == '>' or door_surroundings[0][1] == '(':
        print("south")
        coord_to_reach[0] = coord_to_reach[0] - 1
        stp = 2
    elif door_surroundings[1][2] == '.' or door_surroundings[1][2] == '@' or door_surroundings[1][2] == '<' or door_surroundings[1][2] == '>' or door_surroundings[1][2] == '(':
        print("west")
        coord_to_reach[1] = coord_to_reach[1] + 1
        stp = 3
    elif door_surroundings[1][0] == '.' or door_surroundings[1][0] == '@' or door_surroundings[1][0] == ' <' or door_surroundings[1][0] == '>' or door_surroundings[1][0] == '(':
        print("est")
        coord_to_reach[1] = coord_to_reach[1] - 1
        stp = 1
    elif door_surroundings[2][1] == '.' or door_surroundings[2][1] == '@' or door_surroundings[2][1] == '<' or door_surroundings[2][1] == '>' or door_surroundings[2][1] == '(':
        print("north")
        coord_to_reach[0] = coord_to_reach[0] + 1
        stp = 0
    else:
        print("error locating door")
        return False, 0, environment, observations

    #wrapping the coords to send to the reach_coordinates now is list[x,y] should be list[[x,y]] due to how usually the coords for a  are taken
    new_coords_to_reach = [coord_to_reach]
    environment, observations = reach_coordinates(environment, observations, new_coords_to_reach)

    flag = 0
    while flag < 5:
        prev_player_pos = char_pos(observations, '@')
        environment.step(stp)
        algorithm_steps+=1
        if prev_player_pos != char_pos(observations, '@'):
            hero_steps +=1
            break
        flag+=1
        print("door tryed n. ", flag)

    environment.render()
    return True, stp, environment, observations

def allign_to_closest_opening(observations, environment, openings):
    coords = get_closest_opening(openings, observations)
    if coords == [0, 0]:
        coords = get_closest_opening(openings, observations, False)
    return allign_to_opening(observations, environment, coords=coords)


def walk_corridor(observations, environment, steps, backwards=False):
    
    global algorithm_steps
    global hero_steps

    if backwards == False:
        for step in steps:
            observations, reward, done, info = environment.step(step)
            environment.render()
            algorithm_steps +=1
            hero_steps += 1
    else:
        new_steps = []
        for step in steps:
            if step == 0:
                new_steps.append(2)
            elif step == 1:
                new_steps.append(3)
            elif step == 2:
                new_steps.append(0)
            elif step == 3:
                new_steps.append(1)
        n_steps = len(new_steps)
        for i in range(0, n_steps):
            step = new_steps.pop()
            print(step)
            observations, reward, done, info = environment.step(step)
            environment.render()
            algorithm_steps +=1
            hero_steps += 1

        observations, reward, done, info = environment.step(step)
        environment.render()
        algorithm_steps +=1
        hero_steps += 1

    return observations, environment


def final_check_before_next_iteration(observations, environment, direction):
    player_fov = char_surroundings(observations, char='@')
    dot_cnt = 0

    global algorithm_steps
    global hero_steps

    if player_fov[0][1] == ".":
        dot_cnt += 1
    if player_fov[2][1] == ".":
        dot_cnt += 1
    if player_fov[1][0] == ".":
        dot_cnt += 1
    if player_fov[1][2] == ".":
        dot_cnt += 1

    if dot_cnt < 2:
        if direction == 0 or direction == 2:
            if ((player_fov[0][1] == "." and player_fov[2][1] == "#" and direction == 0) or (
                    player_fov[0][1] == "#" and player_fov[2][1] == "." and direction == 2) or (
                        player_fov[1][0] == "-" and player_fov[1][2] == ".") or (
                        player_fov[1][0] == "." and player_fov[1][2] == "-") or (
                        player_fov[1][0] == "." and player_fov[1][2] == ".")) and (
                    (player_fov[1][2] != " " and player_fov[1][0] != " ") or (
                    player_fov[1][2] != "-" and player_fov[1][0] != "-") or (
                            player_fov[1][2] != "|" and player_fov[1][0] != "-") or (
                            player_fov[1][2] != "-" and player_fov[1][0] != "|")):
                print("room is fine")
            else:
                if (player_fov[0][1] == " " and direction == 0) or (player_fov[2][1] == " " and direction == 2):
                    direction = get_next_direction(direction, player_fov)
                print("new direction checking a ", direction)
                prev_pos = char_pos(observations, '@')
                observations, reward, done, info = environment.step(direction)
                observations, reward, done, info = environment.step(direction)
                environment.render()
                algorithm_steps +=2
                hero_steps +=2
                if prev_pos == char_pos(observations, '@'):
                    if direction == 0:
                        direction = 2
                    else:
                        direction = 0
                    observations, reward, done, info = environment.step(direction)
                    observations, reward, done, info = environment.step(direction)
                    algorithm_steps +=2
                    hero_steps +=2
                environment.render()
                final_check_before_next_iteration(observations, environment, direction)

        elif direction == 1 or direction == 3:
            if ((player_fov[1][2] == "." and player_fov[1][0] == "#" and direction == 3) or (
                    player_fov[1][2] == "#" and player_fov[1][0] == "." and direction == 1) or (
                        player_fov[0][1] == "|" and player_fov[2][1] == ".") or (
                        player_fov[0][1] == "." and player_fov[2][1] == "|") or (
                        player_fov[0][1] == "." and player_fov[2][1] == ".")) and (
                    (player_fov[0][1] != " " and player_fov[2][1] != " ") or (
                    player_fov[0][1] != "|" and player_fov[2][1] != "|") or (
                            player_fov[0][1] != "|" and player_fov[2][1] != "-") or (
                            player_fov[0][1] != "-" and player_fov[2][1] != "|")):
                print("room is fine")
            else:
                if (player_fov[1][2] == " " and direction == 3) or (player_fov[1][0] == " " and direction == 1):
                    direction = get_next_direction(direction, player_fov)
                print("new direction checking ", direction)
                prev_pos = char_pos(observations, '@')
                observations, reward, done, info = environment.step(direction)
                observations, reward, done, info = environment.step(direction)
                environment.render()
                algorithm_steps +=2
                hero_steps +=2
                if prev_pos == char_pos(observations, '@'):
                    if direction == 1:
                        direction = 3
                    else:
                        direction = 1
                    observations, reward, done, info = environment.step(direction)
                    observations, reward, done, info = environment.step(direction)
                    algorithm_steps +=2
                    hero_steps +=2
                observations, environment = final_check_before_next_iteration(observations, environment, direction)
    return observations, environment

def legal_opening(observations, door_coord):
    # this method checks if the selected door is in a reachable position from the player position
    player_pos = char_pos(observations, "@")
    direction = get_direction(player_pos[0], door_coord)
    mod = 0
    if direction == "north":
        mod = -1
    elif direction == "south":
        mod = 1
    else:
        print(direction)
        mod = 0

    if mod != 0:
        while player_pos[0][0] < door_coord[0] - 1 and direction == "south" or player_pos[0][0] > door_coord[
            0] + 1 and direction == "north":
            x, y = player_pos[0]
            if chr(observations['chars'][x + mod][y]) != '.':
                return False
            player_pos[0][0] += mod

    mock_player_pos = [door_coord[0], player_pos[0][1]]
    direction = get_direction(mock_player_pos, door_coord)

    if direction == "east":
        mod = 1
    elif direction == "west":
        mod = -1
    else:
        mod = 0
        print(direction)

    if mod != 0:
        while player_pos[0][1] > door_coord[1] + 1 and direction == "west" or player_pos[0][1] < door_coord[
            1] - 1 and direction == "east":
            x, y = player_pos[0]
            if chr(observations['chars'][x][y + mod]) != '.':
                return False
            player_pos[0][1] += mod

    return True


def get_direction(coords1, coords2):
    lat1, lon1 = coords1
    lat2, lon2 = coords2
    if lat1 > lat2:
        return "north"
    elif lat1 < lat2:
        return "south"
    elif lon1 > lon2:
        return "west"
    elif lon1 < lon2:
        return "east"
    else:
        return "same location"


def solution(env, obs, _verbose=False):
    global algorithm_steps
    global hero_steps
    global last_door_visit
    global verbose

    verbose = _verbose

    algorithm_steps = 0
    hero_steps = 0
    last_door_visit = 0

    stop = False
    
    first_key = False
    first_key_step = 0
    
    first_door = False
    first_door_step = 0
    
    try:
        while not stop and algorithm_steps < 1000:
            algorithm_steps += 1
            found_stairs, env, obs = reach_stairs_down(obs, env)
            if  found_stairs == False:
                stop = False
                found_key, env, obs = pick_key(env, obs)
                if  found_key == True:
                    if first_key == False:
                        first_key = True
                        first_key_step = hero_steps
                    print("got key")

                all_openings = get_all_openings(obs)
                print("all openings: ", all_openings)
                closest_opening = get_closest_opening(all_openings, obs)
                random_state = 42
                if closest_opening == [0, 0]:
                    closest_opening = get_closest_opening(all_openings, obs, False)
                    random_state = 62
                succeed, direction, env, obs = allign_to_closest_opening(obs, env, openings=all_openings)

                if succeed:
                    if not first_door:
                        first_door_step = hero_steps
                    last_door_visit+=1
                    all_openings[str(closest_opening)] = last_door_visit
                    corridor_path, message, direction, obs, env = navigate_corridor(obs, env, direction, [-999, -999], True, random_state)
                    print("corridor_path ", corridor_path)
                    if message == "impasse":
                        print("going back from impasse")
                        obs, env = walk_corridor(obs, env, corridor_path, True)
                    elif message == "room":
                        print(message)
                    else:
                        stop = True
                    print("corridor_path ", corridor_path)
                    print("algorithm_steps ", algorithm_steps)
                    print("hero_steps ", hero_steps)
                    print("openings ", all_openings)
                else:
                    print("COULD NOT ALLIGN")
                    break
                obs, env = final_check_before_next_iteration(obs, env, direction)
            else:
                print("stairs found")
                return True, algorithm_steps, first_key_step, first_door_step, first_door_step+2
    except Exception as e:
        lg.error(e)
    return False, algorithm_steps, first_key_step, first_door_step, first_door_step+2