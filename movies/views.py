from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Rating
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Sum


def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews

    ratings = Rating.objects.filter(movie=movie)
    avgRating = 0.0
    if not ratings.first():
        avgRating = 3.0
    else:
        for rating in ratings:
            avgRating += rating.rating
        avgRating = avgRating / len(ratings)
    template_data['rating'] = avgRating

    if request.user.is_authenticated:
        userRating = Rating.objects.filter(movie=movie, user=request.user).first()
        if userRating:
            template_data['hasRating'] = True
            template_data['userRating'] = userRating.rating
        else:
            template_data['hasRating'] = False
    else:
        template_data['hasRating'] = False
    return render(request, 'movies/show.html',
                  {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment']!= '':
        movie = Movie.objects.get(id=id)
        movie.review_count = movie.review_count + 1
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        movie.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
                      {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    movie = review.movie
    movie.review_count -= 1
    review.delete()
    movie.save()
    return redirect('movies.show', id=id)

@login_required
def report_review(request, movie_id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Report Review by ' + str(review.user)
        template_data['review'] = review
        template_data['movie_id'] = movie_id
        return render(request, 'movies/report_review.html', {'template_data':template_data})
    if request.method == 'POST':
        review.delete()
    return redirect('movies.show', movie_id)

@staff_member_required
def get_top_user(request):
    rankedUsers = (
        User.objects
        .filter(order__isnull=False)
        .annotate(movies_purchased=Sum('order__item__quantity'))
        .order_by('-movies_purchased', 'username')
    )

    topUser = rankedUsers.first()

    template_data = {}
    template_data['title'] = 'Top User'
    template_data['top'] = topUser

    return render(request, 'movies/top_user.html', {'template_data': template_data})

@staff_member_required
def get_top_users(request):
    ranked_users = (
        User.objects
        .filter(order__isnull=False)
        .annotate(movies_purchased=Sum('order__item__quantity'))
        .order_by('-movies_purchased', 'username')
    )
    list_size = request.GET.get('list_size', '').strip()
    if list_size.isdigit() and int(list_size) > 0:
        ranked_users = ranked_users[:int(list_size)]
    
    template_data = {}
    template_data['title'] = 'Top Users'
    template_data['users'] = ranked_users
    template_data['list_size'] = list_size

    return render(request, 'movies/top_users.html', {'template_data': template_data})

@staff_member_required
def get_metrics(request):
    template_data = {}
    movies = Movie.objects.all()
    most_purchased = movies[0]
    most_reviewed = movies[0]
    purchased_max = most_purchased.purchase_count
    reviewed_max = most_reviewed.review_count
    for movie in movies:
        if (movie.purchase_count > purchased_max):
            most_purchased = movie
            purchased_max = most_purchased.purchase_count
        if (movie.review_count > reviewed_max):
            most_reviewed = movie
            reviewed_max = most_reviewed.review_count

    template_data['most_purchased'] = most_purchased
    template_data['most_reviewed'] = most_reviewed

    return render(request, 'movies/metrics.html', {'template_data': template_data})

@login_required
def submit_rating(request, id):
    print("=1 " + str(1==request.POST['oneStar']))
    print("=2 " + str(1==request.POST['twoStar']))
    print("=3 " + str(1==request.POST['threeStar']))
    print("=4 " + str(1==request.POST['fourStar']))
    print("=5 " + str(1==request.POST['fiveStar']))

    if int(request.POST['fiveStar']) == 1:
        score = 5
    elif int(request.POST['fourStar']) == 1:
        score = 4
    elif int(request.POST['threeStar']) == 1:
        score = 3
    elif int(request.POST['twoStar']) == 1:
        score = 2
    else:
        score = 1

    userRating = Rating.objects.filter(movie=Movie.objects.get(id=id), user=request.user).first()
    if userRating:
        print(score)
        userRating.rating = score
    else:
        userRating = Rating(user=request.user, movie=Movie.objects.get(id=id), rating=score)
    userRating.save()
    return redirect('movies.show', id)