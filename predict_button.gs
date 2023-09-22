//PA004 Health Insurance Cross-Sell
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu ('Cross-Sell Predict')
    .addItem('Get Prediction', 'PredictAll')
    .addToUi();
}

host_production = 'pa004-healthinsurancecrosssell.onrender.com'

//Helper Function
function ApiCall(data, endpoint){
  var url = 'https://' + host_production + endpoint;
  var payload = JSON.stringify(data);

  var options = {'method': 'POST', 'contentType': 'application/json', 'payload':payload};

  var response = UrlFetchApp.fetch(url, options);

  //get response
  var rc = response.getResponseCode();
  var responseText = response.getContentText();

  if ( rc!==200){
    Logger.log('Response (%s) %s', rc, responseText);
  }
  else{
    prediction = JSON.parse( responseText );
  }

  return prediction

}

function PredictAll(){
  var ss = SpreadsheetApp.getActiveSheet();
  var titleColumns = ss.getRange('A1:P1').getValues()[0];
  var lastRow = ss.getLastRow()

  var data = ss.getRange('A2'+':'+'P'+lastRow).getValues();

  //iterate rows
  for (row in data){
    var json = new Object();

    //iterate columns
    for (var j=0; j < titleColumns.length; j++){
      json[titleColumns[j]] = data[row][j];
    };

    //list of json to send
    var json_send = new Object();
    json_send['id']                     = json['id']
    json_send['age']                    = json['age']
    json_send['region_code']            = json['region_code']
    json_send['policy_sales_channel']   = json['policy_sales_channel']
    json_send['previously_insured']     = json['previously_insured']
    json_send['annual_premium']         = json['annual_premium']
    json_send['vintage']                = json['vintage']
    json_send['driving_license']        = json['driving_license']
    json_send['vehicle_age']            = json['vehicle_age']
    json_send['vehicle_damage']         = json['vehicle_damage']
    json_send['scored_sales_channel']   = json['scored_sales_channel']
    json_send['vehicle_age_score']      = json['vehicle_age_score']
    json_send['region_score']           = json['region_score']
    json_send['annual_premium_per_day'] = json['annual_premium_per_day']
    json_send['annual_premium_per_age'] = json['annual_premium_per_age']
    json_send['vintage_per_age']        = json['vintage_per_age']

    pred = ApiCall( json_send, '/predict');

    //Send back to Google Sheets
    ss.getRange(Number(row) + 2, 17).setValue(pred[0]['score'])


  };
}