//! The schema-version-keyed column map (spec 058 FR-015): every
//! observation cell addressable by NAME per schema version, so a
//! downstream reader (trainer gate reads, cert readers, probe scripts)
//! never hardcodes a raw index that a bump silently moves.
//!
//! One source per version: the CURRENT version's entries are built from
//! the same offset constants the encoder uses; a RETIRED version's
//! entries are a literal historical table, oracle-tested against its
//! contract's numbers in `tests/schema_five_pins.rs`. Unknown versions
//! and unknown names are errors, never defaults.
//!
//! The maps describe the DEFAULT slot configuration (the served one:
//! kitty 4, chow 2, water 2, sunbeam 2, critter 4) — the only
//! configuration recorded artifacts use. `slot_config` states it, so a
//! reader under a bespoke config can detect the mismatch instead of
//! mis-indexing.
//!
//! Naming: `self.*` and `clock` are ABSOLUTE indices; repeated-block
//! cells (`kitty_row.*`, `chow.*`, `water.*`, `sunbeam.*`, `critter.*`)
//! are STRIDE-RELATIVE — resolve with [`SchemaMap::index`]
//! (`base + slot * stride + relative`). A `*_block`/base name points at
//! the first cell of a multi-cell group (one-hots, message blocks).

use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SchemaMapError {
    UnknownSchemaVersion(u32),
    UnknownCell(String),
    UnknownBlock(String),
    SlotOutOfRange {
        block: &'static str,
        slot: usize,
        count: usize,
    },
}

impl fmt::Display for SchemaMapError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::UnknownSchemaVersion(v) => {
                write!(
                    f,
                    "no column map for schema version {v} (maps exist for 5 and 6)"
                )
            }
            Self::UnknownCell(n) => write!(f, "no cell named '{n}' in this schema version"),
            Self::UnknownBlock(n) => write!(f, "no block named '{n}' in this schema version"),
            Self::SlotOutOfRange { block, slot, count } => {
                write!(
                    f,
                    "slot {slot} out of range for block '{block}' (count {count})"
                )
            }
        }
    }
}

impl std::error::Error for SchemaMapError {}

/// A repeated block: `count` copies of `stride` cells starting at `base`.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct BlockSpec {
    pub name: &'static str,
    pub base: usize,
    pub stride: usize,
    pub count: usize,
}

#[derive(Debug)]
pub struct SchemaMap {
    pub observation_version: u32,
    pub observation_len: usize,
    /// (kitty, chow, water, sunbeam, critter) slot counts this map assumes.
    pub slot_config: (usize, usize, usize, usize, usize),
    pub blocks: &'static [BlockSpec],
    /// `self.*`/`clock` absolute; block-prefixed names stride-relative.
    pub cells: &'static [(&'static str, usize)],
}

impl SchemaMap {
    /// Named cell: absolute for `self.*`/`clock`, stride-relative for
    /// block-prefixed names. Errors on unknown names — never a default.
    pub fn cell(&self, name: &str) -> Result<usize, SchemaMapError> {
        self.cells
            .iter()
            .find(|(n, _)| *n == name)
            .map(|(_, i)| *i)
            .ok_or_else(|| SchemaMapError::UnknownCell(name.to_string()))
    }

    pub fn block(&self, name: &str) -> Result<&BlockSpec, SchemaMapError> {
        self.blocks
            .iter()
            .find(|b| b.name == name)
            .ok_or_else(|| SchemaMapError::UnknownBlock(name.to_string()))
    }

    /// Absolute index of a repeated-block cell: `base + slot*stride + rel`.
    pub fn index(&self, block: &str, slot: usize, cell: &str) -> Result<usize, SchemaMapError> {
        let b = self.block(block)?;
        if slot >= b.count {
            return Err(SchemaMapError::SlotOutOfRange {
                block: b.name,
                slot,
                count: b.count,
            });
        }
        Ok(b.base + slot * b.stride + self.cell(cell)?)
    }
}

/// Schema 5 (spec 049, `specs/049-fog-gen1/contracts/observation-v5.md`):
/// a LITERAL historical table. The encoder no longer derives these
/// numbers once v6 lands; `tests/schema_five_pins.rs` is the oracle that
/// pins every entry against the contract.
static V5: SchemaMap = SchemaMap {
    observation_version: 5,
    observation_len: 408,
    slot_config: (4, 2, 2, 2, 4),
    blocks: &[
        BlockSpec {
            name: "kitty_row",
            base: 85,
            stride: 63,
            count: 4,
        },
        BlockSpec {
            name: "chow",
            base: 337,
            stride: 5,
            count: 2,
        },
        BlockSpec {
            name: "water",
            base: 347,
            stride: 4,
            count: 2,
        },
        BlockSpec {
            name: "sunbeam",
            base: 355,
            stride: 6,
            count: 2,
        },
        BlockSpec {
            name: "critter",
            base: 367,
            stride: 10,
            count: 4,
        },
    ],
    cells: &[
        // Self block (absolute), 0..85.
        ("self.needs.eat", 0),
        ("self.needs.drink", 1),
        ("self.needs.sleep", 2),
        ("self.needs.play", 3),
        ("self.needs.cuddle", 4),
        ("self.needs.bath", 5),
        ("self.happiness", 6),
        ("self.pos.x", 7),
        ("self.pos.y", 8),
        ("self.activity_block", 9),
        ("self.social", 16),
        ("self.in_sunbeam", 17),
        ("self.in_water", 18),
        ("self.progress", 19),
        ("self.distress_block", 20),
        ("self.pursuit_block", 26),
        ("self.traits_block", 28),
        ("self.scene_age", 34),
        ("self.msg_block", 35),
        ("self.memory_block", 65),
        // Kitty row (stride-relative, stride 63).
        ("kitty_row.present", 0),
        ("kitty_row.dx", 1),
        ("kitty_row.dy", 2),
        ("kitty_row.distance", 3),
        ("kitty_row.needs.eat", 4),
        ("kitty_row.needs.drink", 5),
        ("kitty_row.needs.sleep", 6),
        ("kitty_row.needs.play", 7),
        ("kitty_row.needs.cuddle", 8),
        ("kitty_row.needs.bath", 9),
        ("kitty_row.happiness", 10),
        ("kitty_row.activity_block", 11),
        ("kitty_row.partner", 18),
        ("kitty_row.is_my_target", 19),
        ("kitty_row.in_water", 20),
        ("kitty_row.on_sunbeam", 21),
        ("kitty_row.scene_age", 22),
        ("kitty_row.msg_block", 23),
        ("kitty_row.want_block", 53),
        ("kitty_row.answers_me_block", 59),
        // Element slots (stride-relative).
        ("chow.present", 0),
        ("chow.dx", 1),
        ("chow.dy", 2),
        ("chow.distance", 3),
        ("chow.servings", 4),
        ("water.present", 0),
        ("water.dx", 1),
        ("water.dy", 2),
        ("water.distance", 3),
        ("sunbeam.present", 0),
        ("sunbeam.dx", 1),
        ("sunbeam.dy", 2),
        ("sunbeam.distance", 3),
        ("sunbeam.ttl", 4),
        ("sunbeam.occupied", 5),
        ("critter.present", 0),
        ("critter.dx", 1),
        ("critter.dy", 2),
        ("critter.distance", 3),
        ("critter.is_greeble", 4),
        ("critter.heading_block", 5),
        ("critter.is_activity_target", 9),
        // The episode clock (absolute; v5 only — dropped at v6).
        ("clock", 407),
    ],
};

/// Schema 6 (spec 058, contracts/observation-v6.md): DERIVED from the
/// live encoder's offset constants — one source, never a second literal
/// table. `schema_six_pins.rs` asserts the constants against the
/// contract; `tests/schema_map.rs` asserts this map against the pins
/// and the default slot config.
static V6: SchemaMap = {
    use crate::observe::offsets as o;
    const SPATIAL: usize = 4;
    SchemaMap {
        observation_version: 6,
        observation_len: o::SELF_BLOCK + 4 * o::KITTY_SLOT + 2 * 6 + 2 * 5 + 2 * 7 + 4 * 11,
        slot_config: (4, 2, 2, 2, 4),
        blocks: &[
            BlockSpec {
                name: "kitty_row",
                base: o::SELF_BLOCK,
                stride: o::KITTY_SLOT,
                count: 4,
            },
            BlockSpec {
                name: "chow",
                base: o::SELF_BLOCK + 4 * o::KITTY_SLOT,
                stride: 6,
                count: 2,
            },
            BlockSpec {
                name: "water",
                base: o::SELF_BLOCK + 4 * o::KITTY_SLOT + 2 * 6,
                stride: 5,
                count: 2,
            },
            BlockSpec {
                name: "sunbeam",
                base: o::SELF_BLOCK + 4 * o::KITTY_SLOT + 2 * 6 + 2 * 5,
                stride: 7,
                count: 2,
            },
            BlockSpec {
                name: "critter",
                base: o::SELF_BLOCK + 4 * o::KITTY_SLOT + 2 * 6 + 2 * 5 + 2 * 7,
                stride: 11,
                count: 4,
            },
        ],
        cells: &[
            // Self block (absolute). No clock cell exists at v6.
            ("self.needs.eat", 0),
            ("self.needs.drink", 1),
            ("self.needs.sleep", 2),
            ("self.needs.play", 3),
            ("self.needs.cuddle", 4),
            ("self.needs.bath", 5),
            ("self.happiness", 6),
            ("self.wall.n", o::SELF_WALLS),
            ("self.wall.e", o::SELF_WALLS + 1),
            ("self.wall.s", o::SELF_WALLS + 2),
            ("self.wall.w", o::SELF_WALLS + 3),
            ("self.activity_block", o::SELF_WALLS + 4),
            ("self.social", o::SELF_WALLS + 11),
            ("self.in_sunbeam", o::SELF_WALLS + 12),
            ("self.in_water", o::SELF_WALLS + 13),
            ("self.progress", o::SELF_WALLS + 14),
            ("self.distress_block", o::SELF_WALLS + 15),
            ("self.pursuit_block", o::SELF_WALLS + 21),
            ("self.identity_block", o::SELF_IDENTITY),
            ("self.identity.need_rates", o::SELF_IDENTITY),
            ("self.identity.comfort_slack", o::SELF_IDENTITY + 6),
            ("self.identity.consent_line", o::SELF_IDENTITY + 7),
            ("self.identity.favourite_block", o::SELF_IDENTITY + 8),
            ("self.scene_age", o::SELF_SCENE_AGE),
            ("self.msg_block", o::SELF_MSG_BLOCK),
            ("self.memory_block", o::SELF_MEMORY),
            ("self.waypoint_block", o::SELF_WAYPOINT),
            ("self.dirt_reserve_block", o::SELF_DIRT_RESERVE),
            // Kitty row (stride-relative, stride 58).
            ("kitty_row.present", 0),
            ("kitty_row.bearing_x", 1),
            ("kitty_row.bearing_y", 2),
            ("kitty_row.linear", 3),
            ("kitty_row.log", 4),
            ("kitty_row.bath", o::ROW_BATH),
            ("kitty_row.activity_block", o::ROW_BATH + 1),
            ("kitty_row.partner", o::ROW_BATH + 8),
            ("kitty_row.is_my_target", o::ROW_BATH + 9),
            ("kitty_row.in_water", o::ROW_WATER_BIT),
            ("kitty_row.on_sunbeam", o::ROW_SUNBEAM_BIT),
            ("kitty_row.scene_age", o::ROW_SCENE_AGE),
            ("kitty_row.msg_block", o::ROW_MSG_BLOCK),
            ("kitty_row.want_block", o::ROW_INTENSITY),
            ("kitty_row.answers_me_block", o::ROW_ANSWERS_ME),
            // Element slots: present + the spatial group, then v5 extras.
            ("chow.present", 0),
            ("chow.bearing_x", 1),
            ("chow.bearing_y", 2),
            ("chow.linear", 3),
            ("chow.log", 4),
            ("chow.servings", 1 + SPATIAL),
            ("water.present", 0),
            ("water.bearing_x", 1),
            ("water.bearing_y", 2),
            ("water.linear", 3),
            ("water.log", 4),
            ("sunbeam.present", 0),
            ("sunbeam.bearing_x", 1),
            ("sunbeam.bearing_y", 2),
            ("sunbeam.linear", 3),
            ("sunbeam.log", 4),
            ("sunbeam.ttl", 1 + SPATIAL),
            ("sunbeam.occupied", 1 + SPATIAL + 1),
            ("critter.present", 0),
            ("critter.bearing_x", 1),
            ("critter.bearing_y", 2),
            ("critter.linear", 3),
            ("critter.log", 4),
            ("critter.is_greeble", 1 + SPATIAL),
            ("critter.heading_block", 1 + SPATIAL + 1),
            ("critter.is_activity_target", 1 + SPATIAL + 5),
        ],
    }
};

/// The column map for one observation schema version.
pub fn column_map(version: u32) -> Result<&'static SchemaMap, SchemaMapError> {
    match version {
        5 => Ok(&V5),
        6 => Ok(&V6),
        v => Err(SchemaMapError::UnknownSchemaVersion(v)),
    }
}
