$(document).ready(function() {
    $('#calendar').fullCalendar({
        events: function(start, end, timezone, callback) {
            $.ajax({
                url: '/reservations/',
                success: function(data) {
                    var events = data.reservations.map(function(reservation) {
                        return {
                            title: reservation.municipality,
                            start: reservation.date,
                            url: '/create_client_reservation/' + reservation.id + '/'
                        };
                    });
                    callback(events);
                },
                error: function(xhr, status, error) {
                    console.error('Error fetching reservations:', error);
                }
            });
        }
    });
});