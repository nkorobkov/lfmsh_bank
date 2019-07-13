function showTransaction(transactionId) {
    console.log("show transaction" + transactionId);
    var tableRow = $('#trans-info-{}'.replace('{}', transactionId));
    var tableSpace = $('#trans-info-{} > td'.replace('{}', transactionId));
    tableRow.toggle();
    console.log(tableSpace.html().length);
    if (tableSpace.html().length === 0) {
        $.ajax({
            type: 'get',
            url: '/getTransactionHTML/',
            data: {
                'trans_id': transactionId,
            },
            success: function (data) {

                // append html to the posts div
                tableSpace.html(data.transactionHTML);
            },
            error: function (xhr, status, error) {
                console.log("error loading trans " + transactionId);

            }
        });
    }

}