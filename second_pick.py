def second_pick(crossed_hab_line, off_level_two, storm_lemons,
                storm_oranges, lemons, oranges, themself, level_one,
                level_two, level_three, climb_compatability,
                success_rate, speed, agility, knocking,
                number_of_knocks, opposing_alliance_drops,
                avg_opposing_alliance_drops, docking,
                seconds_added_to_cycle, points_per_cycle_per_second,
                path_blocking):
    '''calculates all the data fields necessary for determining
    the second pick'''

    sand_storm_score = (crossed_hab_line + off_level_two*3) + storm_lemons*2 + storm_oranges*3
    teleops_score = 400*lemons*2 + 500*oranges*3
    end_game_score = 300*themself*(level_one*3 + level_two*6 + level_three*12) + (1 - 300) * climb_compatability*12 * success_rate
    driver_ability = 200*(100*speed)+((1-100)*agility)
    defense_ability = knocking*number_of_knocks*(opposing_alliance_drops - avg_opposing_alliance_drops)+docking*seconds_added_to_cycle*points_per_cycle_per_second + path_blocking*seconds_added_to_cycle*points_per_cycle_per_second
    return 'Sandstorm score:', sand_storm_score, 'Teleops score:', teleops_score, 'Final score:', end_game_score, 'Driver ability:', driver_ability, 'Defense ability:', defense_ability
