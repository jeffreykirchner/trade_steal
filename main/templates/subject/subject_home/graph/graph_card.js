{% load static %}

{%include "subject/subject_home/graph/pixi_setup.js"%}
{%include "subject/subject_home/graph/pixi_interface.js"%}
{%include "subject/subject_home/graph/transfer_goods.js"%}

/**
 * set the visibility of all feilds and houses
 */
setFieldHouseVisbility(value){
    session_players = app.$data.session.session_players;
    for(let i=0;i<session_players.length;i++)
    {
        if(session_players[i].houseContainer)
        {
            session_players[i].houseContainer.visible = value;
        }

        if(session_players[i].fieldContainer)
        {
            session_players[i].fieldContainer.visible = value;
        }

        if(session_players[i].avatarContainer)
        {
            session_players[i].avatarContainer.visible = value;
        }
    }
},