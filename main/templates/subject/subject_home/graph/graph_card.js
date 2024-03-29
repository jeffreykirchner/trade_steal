{% load static %}

{%include "subject/subject_home/graph/pixi_setup.js"%}
{%include "subject/subject_home/graph/pixi_interface.js"%}
{%include "subject/subject_home/graph/transfer_goods.js"%}

/**
 * set the visibility of all feilds and houses
 */
setFieldHouseVisbility: function setFieldHouseVisbility(value){
    session_players = app.session.session_players;
    for(let i=0;i<session_players.length;i++)
    {
        if(house_containers[i])
        {
            house_containers[i].visible = value;
        }

        if(field_containers[i])
        {
            field_containers[i].visible = value;
        }

        if(avatar_containers[i])
        {
            avatar_containers[i].visible = value;
        }
    }
},

