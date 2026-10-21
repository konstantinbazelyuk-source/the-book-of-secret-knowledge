# FR-NIA / Figurobot: engineering research for Alita, Kokoro and Ripple

Research date: 2026-10-20. Scope: public manufacturer specifications, public patents, public code, and an integration feasibility assessment. No FR-NIA hardware or software was available for laboratory testing.

## Executive result

Figurobot FR-NIA is advertised as a 28 cm (11-inch) desktop expressive robot with 10 degrees of freedom (7 facial and 3 neck), a Debian-based operating system, 64-bit quad-core ARM Cortex-A53 1.5 GHz CPU, Mali-G31 MP2 GPU, 1 GB RAM, 16 GB storage, dual-band Wi-Fi, Bluetooth 5.0, USB-C data/charging, camera, dual microphones, speakers, and a silicone face. The exact FR-NIA protocol, firmware, SDK, schematic, and public source repository were **not found** in the public materials examined.

A public Lingtong Robotics patent (CN120828427A) details a *related* compact robotic head architecture with Wi-Fi receiving external control instructions, MCU processing, motor command distribution, and feedback. This is direct evidence for a control architecture developed by the manufacturer, **not proof** the shipping FR-NIA implements that exact patent or exposes it to customers.

**Engineering decision:** FR-NIA might be a very suitable physical face for Alita/Kokoro, but purchasing specifically for external programmatic control should wait until Figurobot confirms an SDK/API, supported local-control protocol or documented integration path. App control and keyframe editing alone do not establish a documented third-party programming interface.

## 1. Manufacturer's published specifications (not independently benchmarked)

| Parameter | Advertised value |
| --- | --- |
| Product | FR-NIA, stationary desktop expressive bust |
| Height | 28 cm / 11 in |
| Actuation | 10 DOF; 7 facial + 3 neck |
| Processor | Quad-core Cortex-A53 1.5 GHz, 64 bit |
| GPU | Mali-G31 MP2 |
| RAM / storage | 1 GB / 16 GB |
| OS | Debian-based |
| Connectivity | 2.4/5 GHz Wi-Fi, Bluetooth 5.0 |
| USB | USB-C data + charging |
| Camera | 2 MP, 90-degree field of view |
| Sound | Dual microphones with noise cancellation; 2 x 2W/4Ω speakers |
| Face | Liquid silicone |
| Power | 5V/2A input |
| Battery | Listed as dual 2500mAh cells, nominal 7.4V, up to 5 hours |
| Claimed servo performance | peak torque 20 kg.cm (about 2 N.m); torque density 50 N.m/kg; backlash <0.5 degrees |

Primary source: https://us.figurobot.com/en-jp/products/nia-bionic-facial-robot

**Hardware notes:** A Debian-based OS is not equivalent to root/SSH access or an open hardware platform. A USB-C *data* connection is not evidence that it exposes serial, ADB, Ethernet, or arbitrary command access. Likewise Wi-Fi/Bluetooth connectivity does not prove a public API. The 10-DOF configuration of FR-NIA is distinct from the company's approximately 60-cm NIA-FR02 humanoid platform and its 27/34-DOF marketing materials.

## 2. Public patents verified

1. **CN120828427A** — "High-integration multi-degree-of-freedom head driving mechanism for small humanoid robot and control method". Applicant: Lingtong Robotics Shanghai. Filed 2025-08-13; published 2025-10-24. Original public description specifies worm/worm gear and linkages; eye horizontal and vertical movement, head yaw/nod; MCU, Wi-Fi, dual microphones, speaker, incoming external control instructions and motor-command feedback. Patent enumerates 4 drive motors, not FR-NIA's claimed 10-DOF arrangement. **Related technical design, not confirmed FR-NIA production schematic.** https://patents.google.com/patent/CN120828427A/zh
2. **CN113305867A/B** — "Robot control circuit and control system supporting multiple AI programming methods". Lingtong Robotics Shanghai and Shanghai Nashen Robot appear as current assignees; original applicant Shanghai Nashen. Describes a main control unit integrating interfaces to an external programmable board, sensors, driving motors and servos. The presence of an open-hardware interface in this patent does not guarantee the current FR-NIA contains or exposes it. https://patents.google.com/patent/CN113305867A/zh
3. **CN111267130B** — Wearable lip-position/mouth-shape capturing device and use method, now listed under Lingtong Robotics Shanghai. Relevant to motion capture and lip synchronization research; not verified as FR-NIA's production method. https://patents.google.com/patent/CN111267130B/en
4. **CN309843236S** — Humanoid robot head, industrial-design patent owned by Lingtong Robotics Shanghai. Protects appearance, not complete control electronics. https://patents.google.com/patent/CN309843236S/zh
5. **CN309885215S** — Humanoid robot dual-joint servo, industrial-design patent owned by Lingtong Robotics Shanghai. Appearance rather than a firmware specification. https://patents.google.com/patent/CN309885215S/en
6. **CN309832767S** — Humanoid robot single-joint servo, industrial-design patent owned by Lingtong Robotics Shanghai. https://patents.google.com/patent/CN309832767S/en
7. **CN224601683U** — Media reporting identifies a Lingtong Robotics patent on a robot head support frame and motor-mount arrangement, reportedly granted 2026-08. Original registry page was not retrieved in this investigation, so this is marked **secondary-source only**. https://m.jrj.com.cn/madapter/finance/2026/08/07114258041156.shtml

**Patent-reading boundary:** Public patent descriptions and figures may be studied; that does not itself grant a patent license or permission to reproduce commercially protected claims. Patents describe disclosed embodiments, not necessarily exact shipped PCB layouts, firmware binaries, source code or calibration data.

## 3. Software control: what is and isn't established

**Described by manufacturer / industry reporting**
- Figurobot phone-app integration for real-time manipulation of movement and expression.
- Motion recording, keyframe-based editing and custom expressions.
- Personalization of appearance and character behavior.
- Manufacturer filing CN120828427A includes receiving external commands over Wi-Fi in its described MCU-based architecture.

**Not verified as available for the shipping FR-NIA**
- Public manufacturer SDK for arbitrary host-issued commands.
- USB serial driver or device protocol, local network/WebSocket/REST/BLE service interface.
- Access to low-level joint states, encoder readings, servo calibration, current/temperature and failsafe.
- Ability to bypass/replace the built-in language model with Kokoro/Ripple or stream independent audio to speakers.
- Root/SSH access, firmware images, downloadable schematics or source code.
- API credentials, app developer documentation or published warranty policy for software modifications.

Official marketing: https://us.figurobot.com/
Independent contemporaneous summary: https://www.humanoidsdaily.com/news/figurobot-fr-nia-expressive-ai-companion-kickstarter

## 4. Proposed integration (not yet tested on FR-NIA)

### Host-first architecture

```
Kokoro / Alita conversational control and user-facing application
                |
Ripple computational components, memory and state management
                |
Decision outputs: say(text), expression(name, intensity),
                  gaze(target), head_pose(yaw, pitch, roll), stop()
                |
Documented adapter layer (ONLY after manufacturer protocol is verified)
                |
Local Wi-Fi, USB or Bluetooth transport (to be selected empirically)
                |
FR-NIA embedded controller -> existing motor, audio and sensor hardware
```

A reasonable host machine is a Dell laptop. FR-NIA's listed RAM/CPU are modest by contemporary LLM standards; any substantial local model may be better run externally. The eventual bridge should normalize joints/expressions without falsely assuming each advertised degree of freedom has a separately exposed direct control channel.

### Concrete integration acceptance tests
1. Confirm an authorized developer interface and read its official command contract.
2. Discover device and establish a documented authenticated connection over the supported transport.
3. Read device model, firmware version, motor-state availability, and control limits.
4. Send a manufacturer-supported neutral/rest expression; verify actual motion and return-to-rest.
5. Send one documented calibrated movement; measure latency, repeatability and stop response.
6. Test independent speech and motion commands, audio I/O, network interruption, and replay prevention.
7. Confirm off-line operation, privacy behavior, firmware-update policy and warranty restrictions.
8. Only then connect Kokoro/Ripple behavioral output to an actual working hardware adapter.

No command packet bytes, motor IDs, port numbers or endpoints are invented here.

## 5. Verified source-code alternative for development

**Pollen Robotics Reachy Mini** has publicly accessible, maintained control software and a real Python/JavaScript SDK that can connect to its hardware. It is **a different robot**, not a FR-NIA compatibility solution. Its source code can serve as a working reference for designing Kokoro's host-controller interface, state handling, safety architecture and voice/motion integration, even before purchasing FR-NIA.

- Main repository: https://github.com/pollen-robotics/reachy_mini
- SDK guide: https://github.com/pollen-robotics/reachy_mini/blob/main/docs/source/SDK/quickstart.md
- Python SDK source: https://github.com/pollen-robotics/reachy_mini/blob/main/src/reachy_mini/reachy_mini.py
- JavaScript SDK: https://github.com/pollen-robotics/reachy_mini/blob/main/ts/README.md

Verify dependency licenses independently before copying code into a differently licensed Ripple/Kokoro repository.

## 6. Price / delivery diligence as of 2026-10-20

Figurobot's October 19 GlobeNewswire release advertises $599 starting early-bird price and Lite/Pro/Pro Max levels. The manufacturer's reservation page lists $1 deposit for a $799 Kickstarter price, $20 deposit for $699, and $999 MSRP. These offers are not necessarily comparable versions. The manufacturer makes clear reservation deposits are **not delivery of a robot** and that shipping is additional. Kickstarter live status and a fulfilled shipping date were not independently verified.

Press release: https://markets.businessinsider.com/news/stocks/figurobot-launches-fr-nia-a-11-inch-bionic-ai-companion-robot-bringing-intelligent-interaction-into-everyday-life-1036637933
Manufacturer listing: https://us.figurobot.com/en-jp/products/nia-bionic-facial-robot
Campaign page: https://www.kickstarter.com/projects/figurobot-nia/fr-nia-the-worlds-first-portable-expressive-robot

## 7. Specific technical questions for Figurobot before purchase

Send to support@figurobot.com:

1. Is FR-NIA (specifically the 28 cm/10-DOF model) supported by an official SDK/API for external Python, C++, JavaScript or ROS2 control? Can you provide the documentation and sample client?
2. Can an external laptop control face, eyes and neck in real time over **local** Wi-Fi, USB or Bluetooth without the Figurobot app/cloud? What are the exact protocol, authentication requirements, control frequency and latency guarantees?
3. Does the API expose each of the 10 motor channels or only presets/keyframed sequences? Are joint limits, homing, position feedback, and emergency stop documented?
4. Can I route my own assistant's generated speech to FR-NIA's speakers and optionally access the microphone and camera streams?
5. Can I run my own conversational controller and memory system rather than the included companion model? Are any integrations dependent on subscription services or tokens?
6. Is there documentation for firmware images, recovery, debug logs, system updates, permitted custom software, and warranty implications?
7. Which model/tier includes the control and programming capabilities, what is the full delivered price, and what is the ship date and return policy?

## Verdict

FR-NIA is an excellent *candidate in appearance and advertised peripheral hardware*. Its actual usefulness as Alita/Kokoro's controllable physical endpoint is **unproven** until public programming access or confirmed vendor cooperation is obtained. The strongest immediate source material is CN120828427A plus the manufacturer's real-time app-control descriptions. Reachy Mini provides concrete existing source code and documented APIs for building the software side now, independently of FR-NIA procurement.