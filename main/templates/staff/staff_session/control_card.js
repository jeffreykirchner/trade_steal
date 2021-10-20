/**start the experiment
*/
start_experiment(){
    app.$data.working = true;
    app.sendMessage("start_experiment", {"sessionID" : app.$data.sessionID});
},

/** take start experiment response
 * @param messageData {json}
*/
takeStartExperiment(messageData){
    app.takeGetSession(messageData);
},

/**reset experiment, remove all bids, asks and trades
*/
reset_experiment(){
    if (!confirm('Reset session? All bids and offers will be removed.')) {
        return;
    }

    app.$data.working = true;
    app.sendMessage("reset_experiment", {"sessionID" : app.$data.sessionID});
},

/** take reset experiment response
 * @param messageData {json}
*/
takeResetExperiment(messageData){
    app.takeGetSession(messageData);
},

/**advance to next period
*/
next_period(){
    if (app.$data.session.current_period == app.$data.session.parameter_set.number_of_periods)
    {
        if (!confirm('Complete experiment?')) {
            return;
        }
    }
    else
    {
        if (!confirm('Advance to next period?')) {
            return;
        }
    }

    app.$data.working = true;
    app.sendMessage("next_period", {"sessionID" : app.$data.sessionID});
},

/** take next period response
 * @param messageData {json}
*/
takeNextPeriod(messageData){
    
    app.$data.session.current_period = messageData.data.current_period;
    app.$data.session.finished = messageData.data.finished;

    app.updateMoveOnButtonText();

    if(app.$data.session.finished)
    {
        app.$data.session.current_period = 1;
    }
},