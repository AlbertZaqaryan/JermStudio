const modal = document.getElementById("booking-modal");
const overlay = document.getElementById("booking-modal-overlay");
const closeButton = document.getElementById("close-booking-modal");
const roomLabel = document.getElementById("selected-room-label");
const calendarContainer = document.getElementById("calendar-container");
const timeSlotsContainer = document.getElementById("time-slots");
const bookingForm = document.getElementById("booking-form");
const feedback = document.getElementById("booking-feedback");
const stepButtons = document.querySelectorAll(".booking-step");
const bookingPanels = document.querySelectorAll(".booking-panel");

const bookingState = {
    roomId: null,
    roomName: null,
    selectedDate: null,
    selectedTime: null,
    availableDates: new Set(),
    availableSlots: [],
};

function getCSRFToken() {
    const cookies = document.cookie.split(";");
    for (const cookie of cookies) {
        const trimmed = cookie.trim();
        if (trimmed.startsWith("csrftoken=")) {
            return decodeURIComponent(trimmed.slice("csrftoken=".length));
        }
    }
    return "";
}

function modalText(key, fallback) {
    return modal.dataset[key] || fallback;
}

function setStep(step) {
    stepButtons.forEach((button) => {
        const isActive = Number(button.dataset.step) === step;
        button.classList.toggle("bg-brand-500/10", isActive);
        button.classList.toggle("border-brand-500/60", isActive);
        button.classList.toggle("text-orange-900", isActive);
        button.classList.toggle("border-orange-200", !isActive);
        button.classList.toggle("text-orange-700", !isActive);
    });

    bookingPanels.forEach((panel, index) => {
        panel.classList.toggle("hidden", index !== step - 1);
    });
}

function openModal(roomId, roomName) {
    bookingState.roomId = roomId;
    bookingState.roomName = roomName;
    bookingState.selectedDate = null;
    bookingState.selectedTime = null;
    feedback.classList.add("hidden");
    feedback.textContent = "";
    const roomPrefix = modal.dataset.roomPrefix || "Selected room";
    roomLabel.textContent = `${roomPrefix}: ${roomName}`;
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    document.body.style.overflow = "hidden";
    setStep(1);
    loadAvailableDates();
}

function closeModal() {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
    document.body.style.overflow = "";
}

async function loadAvailableDates() {
    calendarContainer.innerHTML = `<p class='text-orange-700 col-span-full'>${modalText("loadingDates", "Loading available dates...")}</p>`;
    const response = await fetch("/api/available-dates/?days=60");
    const data = await response.json();
    bookingState.availableDates = new Set(data.available_dates || []);
    renderCalendar();
}

function renderCalendar() {
    calendarContainer.innerHTML = "";
    const today = new Date();
    for (let i = 0; i <= 60; i += 1) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        const iso = date.toISOString().split("T")[0];
        const isAvailable = bookingState.availableDates.has(iso);

        const button = document.createElement("button");
        button.type = "button";
        button.textContent = date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
        button.className = [
            "rounded-lg",
            "px-1.5",
            "py-1.5",
            "text-[10px]",
            "leading-tight",
            "sm:rounded-xl",
            "sm:px-3",
            "sm:py-2",
            "sm:text-xs",
            "font-medium",
            "transition",
            isAvailable
                ? "bg-orange-50 hover:bg-orange-100 border border-orange-200 text-orange-900"
                : "cursor-not-allowed bg-orange-50/60 text-orange-300 border border-orange-100",
        ].join(" ");

        if (isAvailable) {
            button.addEventListener("click", async () => {
                bookingState.selectedDate = iso;
                await loadTimeSlots(iso);
                setStep(2);
            });
        } else {
            button.disabled = true;
        }

        calendarContainer.appendChild(button);
    }
}

async function loadTimeSlots(date) {
    timeSlotsContainer.innerHTML = `<p class='text-orange-700 col-span-full'>${modalText("loadingSlots", "Loading available slots...")}</p>`;
    const response = await fetch(`/api/available-slots/?date=${date}`);
    const data = await response.json();
    bookingState.availableSlots = data.available_slots || [];
    renderTimeSlots();
}

function renderTimeSlots() {
    timeSlotsContainer.innerHTML = "";
    if (bookingState.availableSlots.length === 0) {
        const text = document.createElement("p");
        text.textContent = modalText("noSlots", "No slots available for this date. Please choose another day.");
        text.className = "col-span-full text-sm text-orange-700";
        timeSlotsContainer.appendChild(text);
        return;
    }

    bookingState.availableSlots.forEach((slot) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = slot;
        button.className =
            "rounded-lg border border-orange-200 bg-orange-50 px-2 py-1.5 text-xs text-orange-900 transition hover:bg-orange-100 sm:rounded-xl sm:px-3 sm:py-2 sm:text-sm";
        button.addEventListener("click", () => {
            bookingState.selectedTime = slot;
            setStep(3);
        });
        timeSlotsContainer.appendChild(button);
    });
}

async function submitBooking(event) {
    event.preventDefault();
    if (!bookingState.selectedDate || !bookingState.selectedTime) {
        feedback.className = "rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm";
        feedback.textContent = modalText("selectDateTime", "Please choose a date and time first.");
        return;
    }

    const formData = new FormData(bookingForm);
    const payload = {
        first_name: formData.get("first_name"),
        last_name: formData.get("last_name"),
        email: formData.get("email"),
        phone: formData.get("phone"),
        date: bookingState.selectedDate,
        time: bookingState.selectedTime,
    };

    const response = await fetch("/api/bookings/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
        feedback.className = "rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm";
        feedback.textContent = typeof data.error === "string" ? data.error : modalText("bookingError", "Unable to create booking. Please try again.");
        feedback.classList.remove("hidden");
        return;
    }

    feedback.className = "rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm";
    feedback.textContent = data.message || modalText("bookingSuccess", "Booking confirmed.");
    feedback.classList.remove("hidden");
    bookingForm.reset();
    setTimeout(() => {
        closeModal();
    }, 1100);
}

document.querySelectorAll(".open-booking-modal").forEach((button) => {
    button.addEventListener("click", () => {
        openModal(button.dataset.roomId, button.dataset.roomName);
    });
});

overlay.addEventListener("click", closeModal);
closeButton.addEventListener("click", closeModal);
bookingForm.addEventListener("submit", submitBooking);

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.classList.contains("hidden")) {
        closeModal();
    }
});
