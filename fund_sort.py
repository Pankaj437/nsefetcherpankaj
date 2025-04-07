import json

# List of input files
files = [
    'funds_banknifty_oi_highest_first.json',
    'funds_finnifty_oi_highest_first.json',
    'funds_nifty_oi_highest_first.json',
    'funds_midcpnifty_oi_highest_first.json',
    'funds_niftynxt50_oi_highest_first.json' 
]

# List to store all PE and CE values with metadata from all files
values_list = []

# Process each file
for filename in files:
    try:
        with open(filename, 'r') as file:
            funds_deployed = json.load(file)

        for strike, expiries in funds_deployed['by_strike'].items():
            for expiry, options in expiries.items():
                pe_value = options.get('PE', 0)
                ce_value = options.get('CE', 0)

                # Add PE if non-zero
                if pe_value > 0:
                    values_list.append({
                        'value': pe_value,
                        'type': 'PE',
                        'strike': strike,
                        'expiry': expiry,
                        'source_file': filename
                    })

                # Add CE if non-zero
                if ce_value > 0:
                    values_list.append({
                        'value': ce_value,
                        'type': 'CE',
                        'strike': strike,
                        'expiry': expiry,
                        'source_file': filename
                    })

    except FileNotFoundError:
        print(f"⚠️ File not found: {filename}")
    except json.JSONDecodeError:
        print(f"⚠️ Failed to decode JSON from: {filename}")
    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")

# Sort by value in ascending order
sorted_values = sorted(values_list, key=lambda x: x['value'])

# Save to output JSON file
with open('all_funds_sorted_ascending.json', 'w') as outfile:
    json.dump(sorted_values, outfile, indent=4)

print("✅ Saved all sorted data in ascending order to 'all_funds_sorted_ascending.json'")
