# Raw Data Directory

## Dataset Format

File: `labeled_expenses.csv`

### Columns:
- `id`: Unique identifier
- `text`: Raw expense text (Indonesian)
- `tokens`: Space-separated tokens
- `labels`: BIO tags (space-separated)

### Example:
```csv
id,text,tokens,labels
1,nasi goreng 15000,nasi goreng 15000,B-ITEM I-ITEM B-PRICE
2,2x bakso @12rb,2x bakso @12rb,O B-ITEM O B-PRICE
3,es teh 10k,es teh 10k,B-ITEM I-ITEM B-PRICE
```

## Data Collection Plan

### Week 1-2: Target 2000+ samples

#### Sources:
1. **Manual Creation** (500 samples)
   - Common Indonesian food/drinks
   - Transportation expenses
   - Shopping items

2. **Template Generation** (1000 samples)
   - Pattern: `[item] [price]`
   - Pattern: `[qty]x [item] @[price]`
   - Pattern: `[item] [qty] [price]`

3. **Crowdsourcing** (500 samples)
   - Google Form untuk mahasiswa
   - Kontribusi team members

### Labeling Guidelines:
- Use BIO tagging scheme
- B-ITEM: Beginning of item name
- I-ITEM: Inside item name (continuation)
- B-PRICE: Beginning of price
- I-PRICE: Inside price (continuation)
- O: Other tokens (quantity, connector words)

### Quality Control:
- Cross-validation by 2 team members
- Inter-annotator agreement (IAA) calculation
- Resolve conflicts through discussion