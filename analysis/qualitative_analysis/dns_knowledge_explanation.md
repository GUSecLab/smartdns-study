* SDNS (8) : This indicated that the response describes SDNS setup or functionality and not that of DNS. 
* Protocol\_unclear (5): This code indicates that it is unclear which protocol the participant is describing in their response (DNS or otherwise). This was often due to a response’s overall lack of detail, its lack of descriptions of key concepts within DNS (or a different protocol), or any key terms that uniquely identified the protocol or process described. 
* Don't\_know (4): This code denoted a participants’ response simply stating they do not know how DNS works and not providing much additional detail.
* identifies\_pc\_by\_ip (2): Responses given this code correctly identify that IP addresses are involved, but focuses on their use to identify Internet end users or their PCs rather than the IP address of the server to which such a user may be trying to navigate.
* missing\_details (3): Response provides an incomplete description of the protocol (to the point where it may be tough to ascertain whether they truly are familiar with the protocol/understand what they’re talking about)
* navigation\_to\_website (1): (Similar to maps\_website\_to\_Internet\_name)
* maps\_website\_to\_Internet\_name (1): indicates understanding that some translation between website (URL?) as shown on screen and how it's routed through the Internet, but does not give more specifics.
* maps\_ip\_to\_domain (2): Correctly IDs what DNS provides mapping between, but has the relationship backwards (i.e. queries domain name that goes w/the IP)
* translates\_domains\_for\_browsers (2): Identify that it provides a translation for a domain name, but not what it's translated to. Also incorrectly indicate its scope is limited to web browsers.
* maps\_website\_to\_ip (17): Correctly identify DNS's high level task/functionality, but fail to distinguish between website/url and domain name
* maps\_domain\_to\_ip (15): Correctly ID that DNS translates btw domain name and IP and that domain=input, IP=response/output
* query\_dns\_server (2): Correctly describes steps for DNS resolution, (but at a higher level/less detail than those labeled query\_recursive\_dns - namely does not talk about the distributed res. process - recursive or iterative)
* query\_recursive\_dns (12): identifies that most deployments of DNS are recursive, often has more detailed step-by-step description of the whole resolution process

