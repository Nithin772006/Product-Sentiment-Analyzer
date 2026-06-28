import { useState } from "react";

import { searchProduct } from "../api/productApi";


const initialForm = {
  productName: "",
  platform: "amazon",
};


function Search() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await searchProduct(form);
      setResult(response.data);
    } catch {
      setResult({ message: "Unable to reach backend API." });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="page-section compact">
      <div className="section-heading">
        <p className="eyebrow">Product Search</p>
        <h1>Submit a product for review collection.</h1>
      </div>

      <form className="search-form" onSubmit={handleSubmit}>
        <label>
          Product name
          <input
            name="productName"
            type="text"
            value={form.productName}
            onChange={handleChange}
            placeholder="Example: wireless headphones"
            required
          />
        </label>

        <label>
          Platform
          <select name="platform" value={form.platform} onChange={handleChange}>
            <option value="amazon">Amazon</option>
            <option value="flipkart">Flipkart</option>
          </select>
        </label>

        <button className="primary-button" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Submitting..." : "Submit Search"}
        </button>
      </form>

      {result ? (
        <pre className="response-box">{JSON.stringify(result, null, 2)}</pre>
      ) : null}
    </section>
  );
}

export default Search;
