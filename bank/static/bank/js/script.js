function showTransaction(transactionId, viewer_role) {
    console.log("show transaction" + transactionId);
    var tableRow = $('#trans-info-{}'.replace('{}', transactionId));
    var tableSpace = $('#trans-info-{} > td'.replace('{}', transactionId));
    tableRow.toggle();
    console.log(tableSpace.html().length);
    if (tableSpace.html().length === 0) {
        tableSpace.text("Секундочку ...")
        $.ajax({
            type: 'get',
            url: '/bank/getTransactionHTML/',
            data: {
                'transaction_id': transactionId,
                'viewer_role':viewer_role
            },
            success: function (data) {
                console.log(data);

                tableSpace.html(data['transaction_HTML']);
            },
            error: function (xhr, status, error) {
                tableSpace.text("Что то пошло не так :( Попробуйте позже, или обратитесь к банкиру")


            }
        });
    }

}