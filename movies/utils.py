def get_most_commented(reviews, list_of_reviews):
    max_reviews = 0
    most_commented = ''
    for r in list_of_reviews:
        quantity = reviews[str(r.user)]
        if quantity > max_reviews:
            max_reviews = quantity
            most_commented = str(r.user)
    return most_commented, max_reviews