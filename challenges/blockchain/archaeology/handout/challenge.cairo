#[starknet::contract]
mod get_flag {
    #[storage]
    struct Storage {}
    
    #[external(v0)]
    fn get_flag_part_1(self: @ContractState, s: felt252) -> felt252 {
        if s == /* REMOVED */ {
            0x4e4e537b0000000000000020be1ee1560f645f315f6c3076335f7233346431 + s * s
        } else {
            0
        }
    }

    #[external(v0)]
    fn get_flag_part_2(self: @ContractState, s: felt252) -> felt252 {
        if s == /* REMOVED */ {
            0x6e675efffffffffffffb1c4c291356dd2b50a6260fc018bf36907519a6357d + s * s *s * s
        } else {
            0
        }
    }
}