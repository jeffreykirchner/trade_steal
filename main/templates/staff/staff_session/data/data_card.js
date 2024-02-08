/**send download summary data
*/
downloadSummaryData(){
    app.working = true;
    this.data_downloading = true;
    app.sendMessage("download_summary_data", {});
},

/** take download summary data
 * @param messageData {json}
*/
takeDownloadSummaryData(messageData){

    var downloadLink = document.createElement("a");
    var blob = new Blob(["\ufeff", messageData.status.result]);
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
downloadActionsData(){
    app.working = true;
    this.data_downloading = true;
    app.sendMessage("download_action_data", {});
},

/** take download summary data
 * @param messageData {json}
*/
takeDownloadActionData(messageData){

    var downloadLink = document.createElement("a");
    var blob = new Blob(["\ufeff", messageData.status.result]);
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
downloadRecruiterData(){
    app.working = true;
    this.data_downloading = true;
    app.sendMessage("download_recruiter_data", {});
},

/** take download recruiter data
 * @param messageData {json}
*/
takeDownloadRecruiterData(messageData){

    var downloadLink = document.createElement("a");
    var blob = new Blob(["\ufeff", messageData.status.result]);
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
downloadPaymentData(){
    app.working = true;
    this.data_downloading = true;
    app.sendMessage("download_payment_data", {});
},

/** take download payment data
 * @param messageData {json}
*/
takeDownloadPaymentData(messageData){

    var downloadLink = document.createElement("a");
    var blob = new Blob(["\ufeff", messageData.status.result]);
    var url = URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = "Exchange_Specialization_Payment_Data_Session_" + app.session.id +".csv";

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    this.data_downloading = false;
},

