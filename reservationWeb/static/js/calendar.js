$(document).ready(function() {
    // Initialize the calendar with Lithuanian settings
    $('#calendar').fullCalendar({
        locale: 'lt',
        header: {
            left: 'prev,next',
            center: 'title',
            right: 'today'
        },
        buttonText: {
            today: 'Šiandien',
            month: 'Mėnuo',
            week: 'Savaitė',
            day: 'Diena'
        },
        monthNames: ['Sausis', 'Vasaris', 'Kovas', 'Balandis', 'Gegužė', 'Birželis', 'Liepa', 'Rugpjūtis', 'Rugsėjis', 'Spalis', 'Lapkritis', 'Gruodis'],
        monthNamesShort: ['Sau', 'Vas', 'Kov', 'Bal', 'Geg', 'Bir', 'Lie', 'Rgp', 'Rgs', 'Spa', 'Lap', 'Grd'],
        dayNames: ['Sekmadienis', 'Pirmadienis', 'Antradienis', 'Trečiadienis', 'Ketvirtadienis', 'Penktadienis', 'Šeštadienis'],
        dayNamesShort: ['Sek', 'Pir', 'Ant', 'Tre', 'Ket', 'Pen', 'Šeš'],
        firstDay: 1,  // Monday as first day of week
        themeSystem: 'standard',
        defaultView: 'month',
        height: 'auto',
        contentHeight: 'auto',
        
        // Disable view switching completely
        views: {
            month: {
                // Month view settings
            }
        },
        // Prevent users from changing views
        viewRender: function(view) {
            if (view.name !== 'month') {
                $('#calendar').fullCalendar('changeView', 'month');
            }
        },
        events: function(start, end, timezone, callback) {
            $.ajax({
                url: '/reservations/',
                success: function(data) {
                    var events = data.reservations.map(function(reservation) {
                        // Get the full municipality name instead of the code
                        var municipalityName = getMunicipalityName(reservation.municipality);
                        
                        return {
                            title: municipalityName,
                            start: reservation.date,
                            url: '/create_client_reservation/' + reservation.id + '/',
                            backgroundColor: getColorForMunicipality(reservation.municipality),
                            borderColor: getColorForMunicipality(reservation.municipality),
                            textColor: '#fff'
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
                    if (reservations.length === 0) {
                        $('#reservation-details').html('<p>Jokių rezervacijų šiai dienai nėra.</p>');
                        return;
                    }
                    
                    var reservationList = '<h3>Rezervacijos: ' + date.format('YYYY-MM-DD') + '</h3><ul>';
                    reservations.forEach(function(reservation) {
                        // Use full municipality name here as well
                        var municipalityName = getMunicipalityName(reservation.municipality);
                        reservationList += '<li><strong>' + municipalityName + '</strong>';
                        
                        if (reservation.is_superuser) {
                            reservationList += '<div class="reservation-actions">' +
                                '<a href="/edit_reservation/' + reservation.id + '" class="btn">Redaguoti</a>' +
                                '<a href="/delete_reservation/' + reservation.id + '" class="btn btn-secondary">Ištrinti</a>' +
                                '</div>';
                        }
                        
                        if (reservation.clients.length > 0) {
                            reservationList += '<ul>';
                            reservation.clients.forEach(function(client) {
                                reservationList += '<li>' + client.client_name + ' ' + client.client_last_name + ' - ' + client.selected_time + '</li>';
                            });
                            reservationList += '</ul>';
                        } else {
                            reservationList += '<p><em>Dar nėra klientų rezervacijų</em></p>';
                        }
                        
                        reservationList += '</li>';
                    });
                    reservationList += '</ul>';
                    $('#reservation-details').html(reservationList);
                },
                error: function(xhr, status, error) {
                    console.error('Error fetching reservations:', error);
                    $('#reservation-details').html('<p>Klaida bandant gauti rezervacijų informaciją.</p>');
                }
            });
        },
        // Handle window resize properly
        windowResize: function(view) {
            // Always use month view regardless of screen size
            $('#calendar').fullCalendar('changeView', 'month');
        }
    });
    
    // Helper function to convert municipality codes to full names in Lithuanian
    function getMunicipalityName(code) {
        var municipalities = {
            'ALY': 'Alytus',
            'KAU': 'Kaunas',
            'PAN': 'Panevėžys',
            'KLA': 'Klaipėda',
            'MAR': 'Marijampolė',
            'SIA': 'Šiauliai',
            'TAU': 'Tauragė',
            'TEL': 'Telšiai',
            'UTA': 'Utena',
            'VIL': 'Vilnius',
            'UKM': 'Ukmergė',
            'PRN': 'Prienai'
        };
        return municipalities[code] || code;
    }
    
    // Helper function to assign consistent colors to municipalities
    function getColorForMunicipality(code) {
        var colors = {
            'ALY': '#3498db', // Blue
            'KAU': '#2ecc71', // Green
            'PAN': '#e74c3c', // Red
            'KLA': '#f39c12', // Orange
            'MAR': '#9b59b6', // Purple
            'SIA': '#1abc9c', // Turquoise
            'TAU': '#d35400', // Pumpkin
            'TEL': '#27ae60', // Nephritis
            'UTA': '#e67e22', // Carrot
            'VIL': '#8e44ad',  // Wisteria
            'UKM': '#2d8659', // Forest Green
            'PRN': '#58b368'  // Moss Green
        };
        return colors[code] || '#3498db';
    }
});