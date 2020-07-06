from django.contrib.auth import authenticate
from django.contrib.auth import login as authLogin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from CreditHistorySite.models import CustomUser, CustomUserType, CustomUserProfile, Organization
from CreditHistorySite.src import main
from CreditHistorySite.src.loanie import Loanie
from CreditHistorySite.src.utility import EthAccount


def index(request):
    return render(request, 'index.html')


def login(request):
    if 'POST' != request.method:
        response = render(request, 'login.html')
    else:
        publicKey = request.POST['publickey']
        password = request.POST['password']

        # authenticate
        user = authenticate(request, username=publicKey, password=password)
        if user is not None:

            # 1. determine if account exists
            # HINT: accountExists = AccountsContract.accountExist(publicKey);
            accountExists = False
            if accountExists:

                authLogin(request, user)
                # determine if it's a loanie or organization
                # 3. access keystore

                # 4. privateKey = web3.eth.account.decrypt(keystore, password)

                # 5. access our accounts contract to see its type={loaine, organization}
                isLoanie = False
                if isLoanie:
                    # get loanie loans and pendingLoans to show them
                    loans = None
                    pendingLoans = None
                    response = render(request, 'loanie/home.html', {'loans': loans,
                                                                    'pendingLoans': pendingLoans})

                else:
                    # get organization loans and to show them
                    loans = None
                    response = render(request, 'organization/home.html', {'loans': loans})
            else:
                errorMsg = 'This account does not exist. Please sign up.'
                response = render(request, 'error.html', {'errorMsg': errorMsg})


        else:
            # Return an 'invalid login' error message.
            errorMsg = 'This account does not exist. Please sign up.'
            response = render(request, 'error.html', {'errorMsg': errorMsg})
    return response


# to clean data and navigate after that to the url('org/home');
def orgSignup(request):
    successSignup = False
    if 'POST' != request.method:
        response = render(request, 'organization/signup.html')
    else:
        # Get the form data
        username = request.POST['username']
        email = request.POST['email']
        commercial_no = request.POST['commercial_no']
        password = request.POST['password']

        # validation should go here

        # a. create CustomUser
        customUser = CustomUser(username=username, email=email,
                                type=CustomUserType.Organization.value)
        customUserProfile = CustomUserProfile(customUser)
        customUser.save()

        # b. create the keystore that has the encrypted privatekey
        web3Handler = main.web3Handler
        ethAccount = EthAccount(web3Handler)
        keystore = ethAccount.create(password)  # this creates an account and returns its associated keysotre
        org = Organization(customUser=customUser, commertialNum=commercial_no, keystore=keystore)
        org.save()

        if org.pk is None:
            errorMsg = 'Sorry some error occurred while creating this account!'
            response = render(request, 'error.html', {'errorMsg': errorMsg})
        else:
            # response = redirect('org.home')  # Should pass the data of the
            response = redirect('index')

    return response


# to clean up the data and navigate to the url('loanie/home');
def loanieSignup(request):
    if 'POST' != request.method:
        response = render(request, 'loanie/signup.html')
    else:
        # TEST
        response = render(request, 'error.html', {'errorMsg': 'Tesing! We will redirect you now to Home Page! BYE...'})

    return response


@login_required(login_url='login')
def orgHome(request):
    # show the data of a logged in organization
    return render(request, 'organization/home.html')


@login_required(login_url='login')
def loanieHome(request):
    # I should here have the publickey and password after logining in
    # Then resotre the privatekey from a keystore
    # Then show the loans and pending loans of a user in their home page
    public_key = input("Enter your public key: ")
    private_key = input("Enter your private key: ")
    web3Handler = main.web3Handler
    userContract = main.userContractClass
    accountsContract = main.accountsContractClass
    loanieObj = Loanie(public_key, private_key, web3Handler, userContract)
    loanieObj.buildPendingLoansList(accountsContract)
    pendingLoans = loanieObj.pendingLoansList
    return render(request, 'loanie/home.html', {'pendingLoans': pendingLoans})

