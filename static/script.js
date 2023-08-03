document.addEventListener("DOMContentLoaded", function () {
  // Sample data for events (replace this with your data or fetch it from an API)
  const events = [
    {
      title: "Client Training",
      start: "2023-07-24T07:00:00",
      end: "2023-07-24T09:00:00",
      color: "#55c196",
    },
    {
      title: "Board Meeting",
      start: "2023-07-25T10:00:00",
      end: "2023-07-25T11:00:00",
      color: "#8655c1",
    },
    // Add more event objects as needed
  ];

  // Initialize FullCalendar
  const calendarEl = document.getElementById("calendar");
  const calendar = new FullCalendar.Calendar(calendarEl, {
    plugins: ["dayGrid", "timeGrid", "list"],
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "dayGridMonth,timeGridWeek,timeGridDay,listMonth",
    },
    events: events,
    eventBackgroundColor: "#3a87ad", // Default event background color
    eventClick: function (info) {
      // Handle event click here
      alert("Event clicked: " + info.event.title);
    },
  });

  // Render the calendar
  calendar.render();
});
