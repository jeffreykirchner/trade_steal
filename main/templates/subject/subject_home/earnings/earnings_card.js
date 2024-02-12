/**
 * calc how many goods are being wasted
 */
 calcWaste: function calcWaste(){

    app.potential_earnings = 0;

    good_one = app.session_player.good_one_house.valueOf();
    good_two = app.session_player.good_two_house.valueOf();

    good_one_need = app.session_player.parameter_set_player.parameter_set_type.good_one_amount;
    good_two_need = app.session_player.parameter_set_player.parameter_set_type.good_two_amount;

    while(good_one >= good_one_need && good_two >= good_two_need)
    {
        good_one -= good_one_need;
        good_two -= good_two_need;

        app.potential_earnings += Math.max(good_one_need, good_two_need);
    }

    app.good_one_waste = good_one;
    app.good_two_waste = good_two;
},