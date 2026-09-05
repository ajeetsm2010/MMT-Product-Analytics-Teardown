import csv
import random
from datetime import datetime, timedelta

# ============================================================
# MMT-INSPIRED PRODUCT ANALYTICS TEARDOWN
# Synthetic Dataset Generator
# ============================================================

random.seed(42)

NUM_USERS = 5000

START_DATE = datetime(2026, 1, 1)
END_DATE = datetime(2026, 6, 30)

SEGMENTS = [
    "Solo Explorer",
    "Family/Group",
    "Business"
]

DEVICES = [
    "Android",
    "iOS"
]

DESTINATIONS = [
    "Goa",
    "Delhi",
    "Mumbai",
    "Bengaluru",
    "Jaipur",
    "Hyderabad",
    "Kochi",
    "Pune",
    "Chennai",
    "Kolkata"
]

# ------------------------------------------------------------
# User segment distribution
# ------------------------------------------------------------

SEGMENT_WEIGHTS = [
    0.55,   # Solo Explorer
    0.20,   # Family/Group
    0.25    # Business
]

# ------------------------------------------------------------
# Base hotel attachment probability
#
# These represent the probability that a user adds a hotel
# after seeing the cross-sell recommendation.
# ------------------------------------------------------------

BASE_ATTACHMENT = {
    "Solo Explorer": 0.031,
    "Family/Group": 0.142,
    "Business": 0.080
}

# Variant experiment uplift
VARIANT_LIFT = 0.024


# ============================================================
# Helper Functions
# ============================================================

def random_date(start, end):
    delta = end - start

    return start + timedelta(
        seconds=random.randint(
            0,
            int(delta.total_seconds())
        )
    )


def make_id(prefix, number):
    return f"{prefix}_{number:06d}"


def write_csv(filename, rows, fieldnames):

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# 1. DIM_USERS
# ============================================================

users = []

for i in range(1, NUM_USERS + 1):

    segment = random.choices(
        SEGMENTS,
        weights=SEGMENT_WEIGHTS,
        k=1
    )[0]

    signup_date = random_date(
        datetime(2025, 1, 1),
        datetime(2026, 2, 28)
    ).date()

    users.append({

        "user_id": make_id("USR", i),

        "signup_date": signup_date,

        "user_segment": segment,

        "device_os": random.choice(DEVICES)

    })


# ============================================================
# 2. APP EVENTS + INITIAL BOOKINGS
# ============================================================

events = []

bookings = []

event_counter = 1
booking_counter = 1
session_counter = 1


for user in users:

    # Number of sessions per user
    num_sessions = random.choices(
        [1, 2, 3, 4],
        weights=[0.45, 0.30, 0.18, 0.07],
        k=1
    )[0]


    for _ in range(num_sessions):

        session_id = make_id(
            "SES",
            session_counter
        )

        session_counter += 1


        session_time = random_date(
            START_DATE,
            END_DATE
        )


        # A/B assignment
        experiment_group = random.choice(
            ["Control", "Variant"]
        )


        # ----------------------------------------------------
        # STEP 1 — Flight Search
        # ----------------------------------------------------

        events.append({

            "event_id": make_id(
                "EVT",
                event_counter
            ),

            "session_id": session_id,

            "user_id": user["user_id"],

            "event_name": "flight_search",

            "experiment_group": experiment_group,

            "event_timestamp": session_time

        })

        event_counter += 1


        # ----------------------------------------------------
        # STEP 2 — Flight Selected
        # ----------------------------------------------------

        flight_selected = (
            random.random() < 0.75
        )


        if not flight_selected:
            continue


        selected_time = (
            session_time
            + timedelta(
                minutes=random.randint(2, 15)
            )
        )


        events.append({

            "event_id": make_id(
                "EVT",
                event_counter
            ),

            "session_id": session_id,

            "user_id": user["user_id"],

            "event_name": "flight_selected",

            "experiment_group": experiment_group,

            "event_timestamp": selected_time

        })

        event_counter += 1


        # ----------------------------------------------------
        # STEP 3 — Hotel Cross-Sell Viewed
        #
        # Only a subset of flight users see the hotel
        # cross-sell experience.
        # ----------------------------------------------------

        widget_viewed = (
            random.random() < 0.82
        )


        if not widget_viewed:

            # Some users still complete flight-only booking
            if random.random() < 0.65:

                checkout_time = (
                    selected_time
                    + timedelta(
                        minutes=random.randint(5, 20)
                    )
                )

                events.append({

                    "event_id": make_id(
                        "EVT",
                        event_counter
                    ),

                    "session_id": session_id,

                    "user_id": user["user_id"],

                    "event_name": "checkout_completed",

                    "experiment_group": experiment_group,

                    "event_timestamp": checkout_time

                })

                event_counter += 1


                flight_value = round(
                    random.uniform(2500, 12000),
                    2
                )


                bookings.append({

                    "booking_id": make_id(
                        "BKG",
                        booking_counter
                    ),

                    "user_id": user["user_id"],

                    "flight_booking_value": flight_value,

                    "hotel_booking_value": "",

                    "is_cross_sell_attached": False,

                    "booking_type": "initial",

                    "booking_timestamp": checkout_time

                })

                booking_counter += 1

            continue


        widget_time = (
            selected_time
            + timedelta(
                minutes=random.randint(1, 5)
            )
        )


        events.append({

            "event_id": make_id(
                "EVT",
                event_counter
            ),

            "session_id": session_id,

            "user_id": user["user_id"],

            "event_name": "hotel_cross_sell_viewed",

            "experiment_group": experiment_group,

            "event_timestamp": widget_time

        })

        event_counter += 1


        # ----------------------------------------------------
        # STEP 4 — Hotel Added
        # ----------------------------------------------------

        base_probability = BASE_ATTACHMENT[
            user["user_segment"]
        ]


        add_probability = base_probability


        # Variant treatment
        if experiment_group == "Variant":

            add_probability += VARIANT_LIFT


        hotel_added = (
            random.random() < add_probability
        )


        # ----------------------------------------------------
        # HOTEL ATTACHED
        # ----------------------------------------------------

        if hotel_added:

            add_time = (
                widget_time
                + timedelta(
                    minutes=random.randint(1, 10)
                )
            )


            events.append({

                "event_id": make_id(
                    "EVT",
                    event_counter
                ),

                "session_id": session_id,

                "user_id": user["user_id"],

                "event_name": "hotel_cross_sell_added",

                "experiment_group": experiment_group,

                "event_timestamp": add_time

            })

            event_counter += 1


            # ------------------------------------------------
            # STEP 5 — Checkout
            # ------------------------------------------------

            checkout_time = (
                add_time
                + timedelta(
                    minutes=random.randint(2, 12)
                )
            )


            events.append({

                "event_id": make_id(
                    "EVT",
                    event_counter
                ),

                "session_id": session_id,

                "user_id": user["user_id"],

                "event_name": "checkout_completed",

                "experiment_group": experiment_group,

                "event_timestamp": checkout_time

            })

            event_counter += 1


            flight_value = round(
                random.uniform(2500, 12000),
                2
            )


            hotel_value = round(
                random.uniform(2500, 15000),
                2
            )


            bookings.append({

                "booking_id": make_id(
                    "BKG",
                    booking_counter
                ),

                "user_id": user["user_id"],

                "flight_booking_value": flight_value,

                "hotel_booking_value": hotel_value,

                "is_cross_sell_attached": True,

                "booking_type": "initial",

                "booking_timestamp": checkout_time

            })

            booking_counter += 1


        # ----------------------------------------------------
        # HOTEL NOT ADDED
        # ----------------------------------------------------

        else:

            # User may still complete flight booking
            if random.random() < 0.65:

                checkout_time = (
                    widget_time
                    + timedelta(
                        minutes=random.randint(5, 20)
                    )
                )


                events.append({

                    "event_id": make_id(
                        "EVT",
                        event_counter
                    ),

                    "session_id": session_id,

                    "user_id": user["user_id"],

                    "event_name": "checkout_completed",

                    "experiment_group": experiment_group,

                    "event_timestamp": checkout_time

                })

                event_counter += 1


                flight_value = round(
                    random.uniform(2500, 12000),
                    2
                )


                bookings.append({

                    "booking_id": make_id(
                        "BKG",
                        booking_counter
                    ),

                    "user_id": user["user_id"],

                    "flight_booking_value": flight_value,

                    "hotel_booking_value": "",

                    "is_cross_sell_attached": False,

                    "booking_type": "initial",

                    "booking_timestamp": checkout_time

                })

                booking_counter += 1


# ============================================================
# 3. REPEAT BOOKINGS FOR RETENTION
# ============================================================

initial_bookings = [
    b for b in bookings
    if b["booking_type"] == "initial"
]


users_with_initial_booking = list({
    b["user_id"]
    for b in initial_bookings
})


for user_id in users_with_initial_booking:

    # Repeat booking probability
    if random.random() >= 0.18:
        continue


    user_bookings = [
        b for b in initial_bookings
        if b["user_id"] == user_id
    ]


    if not user_bookings:
        continue


    previous_booking = random.choice(
        user_bookings
    )


    previous_date = (
        previous_booking["booking_timestamp"]
    )


    repeat_date = (
        previous_date
        + timedelta(
            days=random.randint(30, 120)
        )
    )


    if repeat_date > END_DATE:
        continue


    flight_value = round(
        random.uniform(2500, 12000),
        2
    )


    bookings.append({

        "booking_id": make_id(
            "BKG",
            booking_counter
        ),

        "user_id": user_id,

        "flight_booking_value": flight_value,

        "hotel_booking_value": "",

        "is_cross_sell_attached": False,

        "booking_type": "repeat",

        "booking_timestamp": repeat_date

    })

    booking_counter += 1


# ============================================================
# 4. WRITE DATASETS
# ============================================================

write_csv(

    "data/dim_users.csv",

    users,

    [
        "user_id",
        "signup_date",
        "user_segment",
        "device_os"
    ]
)


write_csv(

    "data/fact_app_events.csv",

    events,

    [
        "event_id",
        "session_id",
        "user_id",
        "event_name",
        "experiment_group",
        "event_timestamp"
    ]
)


write_csv(

    "data/fact_bookings.csv",

    bookings,

    [
        "booking_id",
        "user_id",
        "flight_booking_value",
        "hotel_booking_value",
        "is_cross_sell_attached",
        "booking_type",
        "booking_timestamp"
    ]
)


# ============================================================
# 5. GENERATION SUMMARY
# ============================================================

print()
print("==========================================")
print("MMT PRODUCT ANALYTICS DATASET GENERATED")
print("==========================================")

print(f"Users:       {len(users):,}")
print(f"Events:      {len(events):,}")
print(f"Bookings:    {len(bookings):,}")

print(
    f"Initial:     {sum(1 for b in bookings if b['booking_type'] == 'initial'):,}"
)

print(
    f"Repeat:      {sum(1 for b in bookings if b['booking_type'] == 'repeat'):,}"
)

print("==========================================")
