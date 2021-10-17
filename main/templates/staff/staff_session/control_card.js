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
    app.$data.current_visible_period = 1;
    app.$data.show_bids_offers_graph = true;
    app.$data.show_supply_demand_graph = false;
    app.$data.show_equilibrium_price_graph = false;
    app.$data.show_trade_line_graph = false;
    app.$data.show_gains_from_trade_graph = false;
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
    app.$data.current_visible_period = 1;
    app.$data.bid_offer_message = "";
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
    
    app.$data.current_visible_period = app.$data.session.current_period;
    app.$data.bid_offer_message = "";

    app.updateMoveOnButtonText();

    if(app.$data.session.finished)
    {
        app.$data.current_visible_period = 1;
        app.$data.session.current_period = 1;
    }
},