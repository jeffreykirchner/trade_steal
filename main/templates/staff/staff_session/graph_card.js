
{% load static %}

{%include "staff/staff_session/graph/pixi_setup.js"%}
{%include "staff/staff_session/graph/pixi_interface.js"%}
{%include "staff/staff_session/graph/transfer_goods.js"%}


/**
 * Actions
 */

takeUpdateGoods(){
    results = messageData.status.result;

    for(let r=0; r<results.length; r++){
        player_id = results[r].id;

        for(let p=0; p<app.$data.session.session_players.length; p++)
        {
            player = app.$data.session.session_players[p];

            if(player.id == player_id)
            {
                player.good_one_house = results[r].good_one_house;
                player.good_two_house = results[r].good_two_house;

                player.good_one_field = results[r].good_one_field;
                player.good_two_field = results[r].good_two_field;

                player.houseContainer.destroy();
                player.fieldContainer.destroy();

                app.setupSingleHoue(p);
                app.setupSingleField(p);

                break;
            }
        }
    }
},

/**
 * change the town shown
 */
change_town_view(){
    app.destroyPixiPlayers();
    app.setupPixiPlayers();
},