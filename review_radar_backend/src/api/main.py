import os
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv


# PUBLIC_INTERFACE
class Review(BaseModel):
    """Model for incoming user reviews."""
    product_id: str = Field(..., description="Unique product identifier")
    user_id: str = Field(..., description="ID of the submitting user")
    rating: int = Field(..., ge=1, le=5, description="User's rating of the product (1-5)")
    title: str = Field(
        ..., min_length=1, max_length=100, description="Short review title"
    )
    content: str = Field(
        ..., min_length=1, max_length=2048, description="Review body text"
    )


# PUBLIC_INTERFACE
class ProductSearchQuery(BaseModel):
    """Model for product search query."""
    query: str = Field(..., min_length=1, description="Text to search for products")


# PUBLIC_INTERFACE
class ReviewAggregationRequest(BaseModel):
    """Model for aggregated review request."""
    product_id: str = Field(..., description="Unique product identifier")


# PUBLIC_INTERFACE
class AISummaryRequest(BaseModel):
    """Model for requesting an AI summary."""
    product_id: str


# PUBLIC_INTERFACE
class Token(BaseModel):
    """JWT access token response."""
    access_token: str
    token_type: str


# PUBLIC_INTERFACE
class UserCreate(BaseModel):
    email: EmailStr
    password: str


# PUBLIC_INTERFACE
class User(BaseModel):
    id: str
    email: EmailStr


# -- Load environment variables (for Supabase, JWT, etc) --

load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SECRET_KEY = os.getenv('SECRET_KEY', 'changeme')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# Placeholder for Supabase client
class SupabaseClientStub:
    # Replace with an actual client (e.g., supabase_py) - left as stub for structure
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key

    def post_review(self, review: dict):
        # Placeholder to write to Supabase
        pass

    def fetch_reviews(self, product_id: str):
        # Placeholder for fetching reviews from Supabase
        return []

    def create_user(self, email: str, password_hash: str):
        # Stub user creation
        pass

    def get_user_by_email(self, email: str):
        # Stub user lookup (should return user dict or None)
        return None


supabase = SupabaseClientStub(SUPABASE_URL, SUPABASE_KEY)


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the currently authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        # Ideally look up user in DB here. For demo, return stub
        user = {"id": user_id, "email": f"{user_id}@example.com"}
    except JWTError:
        raise credentials_exception
    return user


# ---------------- Routers ---------------- #

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


# PUBLIC_INTERFACE
@auth_router.post("/register", summary="Register a new user", response_model=User)
async def register_user(user: UserCreate):
    """Register a new user (email & password)."""
    # TODO: Implement password hashing, uniqueness check
    if supabase.get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="User already exists")
    # Just a stub: in reality you must hash and store the password securely
    user_id = user.email
    supabase.create_user(email=user.email, password_hash=user.password)
    return User(id=user_id, email=user.email)


# PUBLIC_INTERFACE
@auth_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT token."""
    user = supabase.get_user_by_email(form_data.username)
    # TODO: Verify hashed password
    if not user or form_data.password != "password":  # Placeholder logic!
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["id"]})
    return {"access_token": access_token, "token_type": "bearer"}


products_router = APIRouter(prefix="/products", tags=["Products"])


# PUBLIC_INTERFACE
@products_router.post("/search", summary="Search for products")
async def search_products(query: ProductSearchQuery):
    """Product search, returns list of matching products."""
    # Placeholder for actual search logic/API
    # TODO: Integrate with external product API or database
    return {
        "results": [
            {
                "id": "sku123",
                "name": "Demo Product",
                "description": f"Sample found for query: {query.query}",
            }
        ]
    }


reviews_router = APIRouter(prefix="/reviews", tags=["Reviews"])


# PUBLIC_INTERFACE
@reviews_router.post("/submit", summary="Submit a product review")
async def submit_review(review: Review, user: dict = Depends(get_current_user)):
    """Submit a review for a product."""
    # TODO: Record user.id as author, avoid multi-submits, validate ownership, etc.
    supabase.post_review(review.model_dump())
    return {"message": "Review submitted"}


# PUBLIC_INTERFACE
@reviews_router.post("/aggregate", summary="Aggregate all reviews for a product")
async def aggregate_reviews(request: ReviewAggregationRequest):
    """Aggregate and return all reviews for a product."""
    # Fetch from Supabase and external APIs (stubs)
    db_reviews = supabase.fetch_reviews(request.product_id)
    # TODO: Call external APIs for additional reviews
    external = []  # Placeholder
    # TODO: Calculate aggregate metrics (avg rating, count, etc)
    all_reviews = db_reviews + external
    average_rating = 4.2
    total_reviews = len(all_reviews)
    return {
        "product_id": request.product_id,
        "reviews": all_reviews,
        "aggregate": {
            "average_rating": average_rating,
            "total_reviews": total_reviews,
        },
    }


ai_router = APIRouter(prefix="/ai", tags=["AI"])


# PUBLIC_INTERFACE
@ai_router.post("/summary", summary="Get AI-generated summary for a product")
async def ai_summary(request: AISummaryRequest):
    """Return an AI-generated summary for a product."""
    # Placeholder for calling an AI service/model
    # TODO: Integrate with OpenAI, local LLM, etc.
    return {
        "product_id": request.product_id,
        "summary": "AI-powered summary will appear here.",
    }


# ---------------- Main FastAPI App ---------------- #

# PUBLIC_INTERFACE
app = FastAPI(
    title="Review Radar Backend API",
    description=(
        "Backend API for product search, review aggregation/storage, authentication, "
        "and AI summaries."
    ),
    version="0.1.0",
    contact={
        "name": "ReviewRadar Team",
        "email": "support@reviewradar.com"
    },
    openapi_tags=[
        {"name": "Auth", "description": "User authentication and registration"},
        {"name": "Products", "description": "Search and get product information"},
        {"name": "Reviews", "description": "Submit and aggregate reviews"},
        {
            "name": "AI",
            "description": "AI-generated summaries and insights"
        }
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- Security & Rate Limiting Stubs ---------------- #

@app.middleware("http")
async def add_rate_limiting(request: Request, call_next):
    # PUBLIC_INTERFACE
    """Stub: Rate limiting middleware (should be replaced with real rate limiting)."""
    # TODO: Track IPs, user tokens, time windows, etc.
    response = await call_next(request)
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    # PUBLIC_INTERFACE
    """Add basic security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# Health check endpoint
# PUBLIC_INTERFACE
@app.get("/", tags=["System"])
def health_check():
    """Simple health check endpoint."""
    return {"status": "Healthy"}


app.include_router(auth_router)
app.include_router(products_router)
app.include_router(reviews_router)
app.include_router(ai_router)
