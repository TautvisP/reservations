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
        },
        eventClick: function(event) {
            if (event.url) {
                window.location.href = event.url;
                return false;
            }
        },
        dayClick: function(date) {
            $.ajax({
                url: '/date/' + date.format('YYYY-MM-DD') + '/',
                success: function(data) {
                    var reservations = data.reservations;
                    var reservationList = '<ul>';
                    reservations.forEach(function(reservation) {
                        reservationList += '<li>' + reservation.municipality + ' - ' + reservation.date;
                        if (reservation.is_superuser) {
                            reservationList += ' <a href="/edit_reservation/' + reservation.id + '">Edit</a>';
                            reservationList += ' <a href="/delete_reservation/' + reservation.id + '">Delete</a>';
                        }
                        reservationList += '<ul>';
                        reservation.clients.forEach(function(client) {
                            reservationList += '<li>' + client.client_name + ' ' + client.client_last_name + ' - ' + client.selected_time + '</li>';
                        });
                        reservationList += '</ul>';
                        reservationList += '</li>';
                    });
                    reservationList += '</ul>';
                    $('#reservation-details').html(reservationList);
                },
                error: function(xhr, status, error) {
                    console.error('Error fetching reservations:', error);
                }
            });
        }
    });
});