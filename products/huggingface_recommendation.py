from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

# Load the pre-trained Hugging Face model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = AutoModel.from_pretrained("distilbert-base-uncased")

def get_product_embedding(text):
    """Generate an embedding for the product name or description."""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
        # Get the embedding from the last hidden state
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings.numpy()

def get_recommendations(cart_items, all_products):
    """Find products similar to the ones in the cart."""
    recommendations = []
    cart_embeddings = []

    # Generate embeddings for cart items
    for item in cart_items:
        text = item.product.name + " " + item.product.description
        embedding = get_product_embedding(text)
        cart_embeddings.append(embedding)

    # Compare each product in the catalog with the cart items
    for product in all_products:
        if product not in cart_items:
            product_text = product.name + " " + product.description
            product_embedding = get_product_embedding(product_text)

            # Compare with cart embeddings using cosine similarity
            for cart_embedding in cart_embeddings:
                similarity = cosine_similarity(cart_embedding, product_embedding)
                if similarity > 0.75:  # Threshold for similarity
                    recommendations.append(product)
                    break

    return recommendations
