# FigureMarkets-MCP-Server
An MCP server to make the Figure Markets and Provenance Blockchain data easily available to MCP-enabled AI-Agents.


### Installation

Note: Only tested on a MacOS 15.5 M1 laptop as a local MCP server over stdio.

Install instruction use brew and uv. 
(... use your own and you're on your own ;-) )

This MCP server is tested with and works with Anthropic's Claude desktop for MacOS. Install Claude desktop for MacOS:

```https://claude.ai/download```


The MCP server is implemented with the MCP Python SDK (`https://github.com/modelcontextprotocol/python-sdk`)


Make sure you have homebrew installed.

`https://docs.brew.sh/Installation`

Make sure your python3 is "better" than the one that comes standard with MacOS - if not:

`brew install python3`

Make sure `uv` is installed - if not:

`brew install uv`

Clone this repo someplace on your computer and change directory into the cloned-repo:

```git clone https://github.com/franks42/FigureMarkets-MCP-Server.git```

```cd FigureMarkets-MCP-Server```

Install MCP Python SDK packages with `uv`:

```uv add "mcp[cli]"```

```uv add "httpx[cli]"```

Use `mcp install` to add the MCP server configuration to Claude's config file (`"/Users/$USERNAME/Library/Application\ Support/Claude/claude_desktop_config.json"`):

```uv run mcp install server.py```

If Claude Desktop is (re-)started then it should automatically pick up the new mcp server coordinates.

Under Claude's chat prompt, there is a "Search and tools" button, which should show a list of tools that shows "FigureMarkets" with all the APIs that are available.

You can also test it by asking:

```What is the current HASH price on the Figure Market exchange?```

To test the mcp server standalone thru a webpage use:

```uv run mcp dev server.py```

### Usage

When Claude recognizes the FM mcp server, it will make use of the API when it needs to obtain data from the FM or PB.

For normal interactions, you should just try some of the example questions.

#### When Claude uses the mcp server apis.

In order for Claude to "know" when to call the mcp server's API, it will use the documentation strings of the APIs and the function signatures.

Most important though is the long concise context document in this repo:

`""https://raw.githubusercontent.com/franks42/FigureMarkets-MCP-Server/refs/heads/main/FigureMarketsContext.md"`

Claude is instructed to read this document before using any of the APIs.

It's worthwhile to look at that document if you want to understand better how Claude determines what to use and when. For normal interactions, you should.

#### Example Questions to ask Claude

```What is the current HASH price on the Figure Markets?```

```How about ETH and XRD?```

```How is the overall exchange doing?```

In many cases you'll have question about the assets in your wallet. The wallet is identified by an address, which is a looong incomprehensible number of characters. The easiest way to interact with Claude about your wallet, is to give it a name such that you have to copy and paste it once, like:

```my wallet address is "pb...123"```

After this you can talk about that wallet like:

```How much HASH do i have in my wallet?```

```What assets are in my wallet?```

```Review my wallet.```

```What do you think about my delegation amount?```

```Do I have vesting hash?```

```What does the vesting schedule look like?```

```Analyze my wallet's portfolio.```

Etc., etc...



