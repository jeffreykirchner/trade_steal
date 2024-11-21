/**send download summary data
*/
downloadSummaryData: function downloadSummaryData(){
    app.working = true;
    this.data_downloading = true;
    app.send_message("download_summary_data", {});
},

/** take download summary data
 * @param message_data {json}
*/
take_download_summary_data: function take_download_summary_data(message_data){

    var downloadLink = document.createElement("a");
    var blob = new Blob(["\ufeff", message_data.result]);
    var url = URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = "Exchange_Specialization_Summary_Data_Session_" + app.session.id +".csv";

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    this.data_downloading = false;
},

/**send download summary data
*/
downloadActionsData: function downloadActionsData(){
    app.working = true;
    this.data_downloading = true;
    app.send_message("download_action_data", {});
},

/** take download summary data
 * @param message_data {json}
*/
take_download_action_data: function take_download_action_data(message_data){

    var downloadLink = document.createElement("a");
    var blob = new Blob(["\ufeff", message_data.result]);
    var url = URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = "Exchange_Specialization_Action_Data_Session_" + app.session.id +".csv";

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    this.data_downloading = false;
},

/**send download recruiter data
*/
downloadRecruiterData: function downloadRecruiterData(){
    app.working = true;
    this.data_downloading = true;
    app.send_message("download_recruiter_data", {});
},

/** take download recruiter data
 * @param message_data {json}
*/
take_download_recruiter_data: function take_download_recruiter_data(message_data){

    var downloadLink = document.createElement("a");
    var blob = new Blob(["\ufeff", message_data.result]);
    var url = URL.createObjectURL(blob);
    downloadLink.href = url;

    if(app.session.parameter_set.prolific_mode=='False')
        downloadLink.download = "Exchange_Specialization_Recruiter_Data_Session_" + app.session.id +".csv";
    else
        downloadLink.download = "Exchange_Specialization_Prolific_Data_Session_" + app.session.id +".csv";

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    this.data_downloading = false;
},

/**send download payment data
*/
downloadPaymentData: function downloadPaymentData(){
    app.working = true;
    this.data_downloading = true;
    app.send_message("download_payment_data", {});
},

/** take download payment data
 * @param message_data {json}
*/
take_download_payment_data: function take_download_payment_data(message_data){

    var downloadLink = document.createElement("a");
    var blob = new Blob(["\ufeff", message_data.result]);
    var url = URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = "Exchange_Specialization_Payment_Data_Session_" + app.session.id +".csv";

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    this.data_downloading = false;
},

