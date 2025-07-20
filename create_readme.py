import csv
from dataclasses import dataclass
from ipaddress import IPv4Address

RESULT_FILENAME = 'result.csv'
README_HEADER = (
    "# warp-endpoint-checker\n\n"
    "A repository containing a list of endpoints, grouped by IP pools, available for connecting to the **Cloudflare WARP** service.\n\n"
    "> 🙏 Special thanks to [peanut996](https://github.com/peanut996/CloudflareWarpSpeedTest) for providing the testing tool.\n\n"
    "---\n\n"
    "## 📊 Table of Available IP Addresses by Pool\n\n"
)
MARKDOWN_TABLE_HEADER = (
    "| IP Address | Ports |\n"
    "|------------|-------|\n"
)


@dataclass
class CloudflareEndpoint:
    address: str
    ports: list[str]

    @property
    def markdown_table_row(self):
        return f'| {self.address} | {', '.join(sorted(self.ports, key=int))} |\n'


def load_csv_data() -> list[CloudflareEndpoint]:
    result = []
    with open(RESULT_FILENAME, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            address, port = row['IP:Port'].split(':')

            try:
                existing_endpoint = next(filter(lambda x: x.address == address, result))
                existing_endpoint.ports.append(port)
            except StopIteration:
                result.append(CloudflareEndpoint(address, [port]))

    return result


def split_by_networks(endpoints: list[CloudflareEndpoint]) -> dict[str, list[CloudflareEndpoint]]:
    result = {}
    for endpoint in endpoints:
        network = '.'.join(endpoint.address.split('.')[:3]) + '.0/24'
        if result.get(network) is None:
            result[network] = [endpoint]
        else:
            result[network].append(endpoint)

    return result


def create_readme(endpoints: dict[str, list[CloudflareEndpoint]]) -> None:
    readme = README_HEADER

    readme += f'### 🗂️ Number of IP Pools: {len(endpoints.keys())}\n'
    readme += f'### 🔢 Total Number of Endpoints: {sum(len(endpoint) for endpoint in endpoints.values())}\n\n'
    readme += '---\n'

    for network, endpoints in endpoints.items():
        readme += f'### Pool: `{network}` Available: {len(endpoints)}\n'
        readme += MARKDOWN_TABLE_HEADER
        for endpoint in endpoints:
            readme += endpoint.markdown_table_row
        readme += '---\n'

    with open('README.md', 'w', encoding='utf-8') as readme_file:
        readme_file.write(readme)


if __name__ == '__main__':
    cf_endpoints = load_csv_data()
    cf_endpoints.sort(key=lambda x: IPv4Address(x.address))
    cf_endpoints = split_by_networks(cf_endpoints)
    create_readme(cf_endpoints)
