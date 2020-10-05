import logging

from state_machine import Edge, State

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# in_edges: [Edge] edges that will be added as outgoing edges from the previous state(s).
# end_states: [State] references to the states in states_to_repeat that do not have any
# futher states after them.
# states_to_repeat: [State] all of the states which should have repetition applied to them.
# Retuns new_in_edges, new_end_states, new_states
def apply_repetition(in_edges, end_states, states_to_repeat, repetition, is_optional):
    logger.debug(f'Applying repetition of {repetition} and is_optional of {is_optional} to:\nin_edges={in_edges}\nend_states={end_states}\nstates_to_repeat={states_to_repeat}')
    if not isinstance(in_edges, list):
        in_edges = [in_edges]
    if not isinstance(end_states, list):
        end_states = [end_states]
    if not isinstance(states_to_repeat, list):
        states_to_repeat = [states_to_repeat]

    if not is_optional and repetition == None:
        logger.debug(f'Got request that has no repetition! Returning as-is.')
        return in_edges, end_states, states_to_repeat

    end_state_ids = {state.id for state in end_states}

    # If the batch is optional, that's the same as having 0-1 repetition.
    if is_optional:
        min_reps = 0
        max_reps = 1
    else:
        min_reps, max_reps = repetition
    logger.debug(f'Applying repetition of {min_reps}-{max_reps} to states {states_to_repeat}')

    copies_to_create = max_reps
    if max_reps == float('inf'):
        logger.debug(f'max_reps is inf, making min_reps copies instead and adding self-loop on last copy.')
        copies_to_create = min_reps

    states = [state.clone() for state in states_to_repeat]
    new_end_states = [state for state in states if state.id in end_state_ids]
    iteration_suffix = ''
    for i in range(2, copies_to_create+1):
        iteration_suffix = f'_{i}'
        logger.debug(f'Making copy {i} with suffix {iteration_suffix}.')

        # Copy the in_edges with the new suffix, and add them to the old end_states,
        # in order to link the last copy up to the current copy.
        for edge in in_edges:
            for end_state in new_end_states:
                end_to_start_edge = edge.clone()
                end_to_start_edge.dest += iteration_suffix
                logger.debug(f'Adding end_to_start_edge {end_to_start_edge} to state {end_state}.')
                end_state.add_edge(end_to_start_edge)

        # Copy all of the original states for the new iteration.
        new_end_states = []
        for state in states_to_repeat:
            logger.debug(f'states_to_repeat: {states_to_repeat}')
            state_id = state.id
            n_state_id = f'{state_id}' + iteration_suffix
            logger.debug(f'Copying state {state.id} as {n_state_id}')

            next_state = State(n_state_id, is_automata = state.is_automata)
            # Copy all of the edges for the state, adding the new suffix. Note
            # that there aren't any edges beyond end_states, so we don't have to
            # worry about this going outside of the current copy iteration.
            for edge in state.edges:
                logger.debug(f'Updating edge {edge}.')
                next_edge = edge.clone()
                next_edge.dest += iteration_suffix
                logger.debug(f'Adding edge {next_edge} to new state {next_state.id}')
                next_state.add_edge(next_edge)

            # Append the state to the states list to keep track of it, and add
            # if to the new_end_states if it's a copy of an end state.
            logger.debug(f'Adding state to states: {state}')
            states.append(next_state)
            if state_id in end_state_ids:
                new_end_states.append(next_state)
        logger.debug(f'new_end_states: {new_end_states}')

    logger.debug(f'Finished creating states. Created state IDs are: {[state.id for state in states]}')

    # If we have infinite repetition we obviously can't create infinite states,
    # so we add a self-loop from the end of the last copy to its beginning.
    if max_reps == float('inf'):
        logger.debug(f'Handling skips for infinite max_reps.')
        new_in_edges = []
        for end_state in new_end_states:
            for edge in in_edges:
                repeat_last_copy_edge = edge.clone()
                repeat_last_copy_edge.dest += iteration_suffix
                logger.debug(f'Adding infinite loop edge {repeat_last_copy_edge} to state {end_state.id}')
                end_state.add_edge(repeat_last_copy_edge)
            if min_reps == 0:
                skip_edge = Edge('', end_state.id)
                logger.debug(f'Got optional or 0-min repetition, adding skip edge {skip_edge} to new_in_edges.')
                new_in_edges.append(skip_edge)
        in_edges += new_in_edges
    # If it's not infinite, then we made max_reps states, but any of them beyond
    # min_reps can be skipped, so we add a skip edge from each end state of an
    # optional copy cohort to each end state of the full batch.
    else:
        logger.debug(f'Handling skips for min_reps={min_reps}, max_reps={max_reps}.')

        skip_edges = [Edge('', state.id) for state in new_end_states]
        logger.debug(f'skip_edges: {skip_edges}')

        for i in range(min_reps, max_reps):
            logger.debug(f'Adding skips to copy {i}.')

            if i == 0:
                for end_state in new_end_states:
                    skip_edge = Edge('', end_state.id)
                    logger.debug(f'Got optional or 0-min repetition, adding skip edge {skip_edge} to in_edges.')
                    in_edges.append(skip_edge)
                continue

            state_suffix = f'_{i}'
            if i == 1:
                state_suffix = ''

            ith_end_state_ids = {state.id + state_suffix for state in end_states}
            logger.debug(f'ith_end_state_ids: {ith_end_state_ids}')
            logger.debug(f'states: {states}')
            for state in states:
                if state.id in ith_end_state_ids:
                    for edge in skip_edges:
                        logger.debug(f'Adding skip edge {edge} to state {state.id}')
                        state.add_edge(edge.clone())

    logger.debug(f'Returning:\n  in_edges: {in_edges}\n  new_end_states: {new_end_states}\n  states: {states}')
    return in_edges, new_end_states, states
