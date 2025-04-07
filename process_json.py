import json
import os

# Define lot sizes per index
LOT_SIZES = {
    'BANKNIFTY': 15,
    'NIFTY': 50,
    'FINNIFTY': 40,
    'MIDCPNIFTY': 75,
    'NIFTYNXT50': 25
}

# Helper to guess index name from filename
def infer_index_from_filename(filename):
    name = filename.upper()
    for index in LOT_SIZES:
        if index in name:
            return index
    return 'NIFTY'

# Function to calculate funds
def calculate_funds_deployed(last_price, open_interest, lot_size):
    return last_price * open_interest * lot_size

# Process all JSON files
for filename in os.listdir():
    if filename.endswith('.json'):
        print(f"\n🔍 Processing: {filename}")
        try:
            with open(filename, 'r') as file:
                option_chain = json.load(file)

            index_name = infer_index_from_filename(filename)
            lot_size = LOT_SIZES.get(index_name, 50)

            records = option_chain['records']
            data = records['data']
            spot_price = data[0].get('PE', data[0].get('CE'))['underlyingValue']

            funds_deployed = {
                'spot_price': spot_price,
                'by_strike': {},
                'total': {'PE': 0, 'CE': 0}
            }

            for entry in data:
                strike = entry['strikePrice']
                expiry = entry['expiryDate']
                funds_deployed['by_strike'].setdefault(strike, {})
                funds_deployed['by_strike'][strike].setdefault(expiry, {'PE': 0, 'CE': 0})

                if 'PE' in entry:
                    pe = entry['PE']
                    pe_funds = calculate_funds_deployed(pe['lastPrice'], pe['openInterest'], lot_size)
                    funds_deployed['by_strike'][strike][expiry]['PE'] = pe_funds
                    funds_deployed['total']['PE'] += pe_funds

                if 'CE' in entry:
                    ce = entry['CE']
                    ce_funds = calculate_funds_deployed(ce['lastPrice'], ce['openInterest'], lot_size)
                    funds_deployed['by_strike'][strike][expiry]['CE'] = ce_funds
                    funds_deployed['total']['CE'] += ce_funds

            # Find highest total strike
            strike_totals = {
                strike: sum(opt['PE'] + opt['CE'] for opt in expiries.values())
                for strike, expiries in funds_deployed['by_strike'].items()
            }

            highest_strike, highest_value = max(strike_totals.items(), key=lambda x: x[1])
            sorted_strikes = sorted(
                [(strike, expiries) for strike, expiries in funds_deployed['by_strike'].items() if strike != highest_strike],
                key=lambda x: x[0]
            )

            # Display results
            print(f"📌 Spot Price (underlyingValue): {spot_price:,.2f}")
            print(f"\n💰 Strike with Highest Funds: {highest_strike} (Total: {highest_value:,.2f} INR)")
            print("Details:")
            for expiry, options in sorted(
                funds_deployed['by_strike'][highest_strike].items(),
                key=lambda x: x[1]['PE'] + x[1]['CE'],
                reverse=True
            ):
                print(f"  Expiry: {expiry}")
                print(f"    PE Funds: {options['PE']:,.2f} INR")
                print(f"    CE Funds: {options['CE']:,.2f} INR")
                print(f"    Total: {options['PE'] + options['CE']:,.2f} INR")
            print()

            print("🧾 Funds by Strike & Expiry (sorted):")
            for strike, expiries in sorted_strikes:
                print(f"Strike: {strike}")
                for expiry, options in sorted(expiries.items(), key=lambda x: x[1]['PE'] + x[1]['CE'], reverse=True):
                    print(f"  Expiry: {expiry}")
                    print(f"    PE: {options['PE']:,.2f} INR")
                    print(f"    CE: {options['CE']:,.2f} INR")
                    print(f"    Total: {options['PE'] + options['CE']:,.2f} INR")
                print()

            print("📊 Total Across All Strikes:")
            print(f"  PE: {funds_deployed['total']['PE']:,.2f} INR")
            print(f"  CE: {funds_deployed['total']['CE']:,.2f} INR")

            # Save result with spot price included
            output_name = f"funds_{filename.replace('.json', '')}_oi_highest_first.json"
            with open(output_name, 'w') as outfile:
                json.dump(funds_deployed, outfile, indent=4)
            print(f"✅ Saved to: {output_name}")

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
