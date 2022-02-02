import random
import pytest

from support.utilities import fill_string_with_char
from tests import marks, common_password, unique_password
from tests.base_test_case import SingleDeviceTestCase, MultipleSharedDeviceTestCase, create_shared_drivers
from views.sign_in_view import SignInView
from tests.users import basic_user, transaction_senders, recovery_users

@pytest.mark.xdist_group(name="onboarding_1")
class TestPublicChatOneDeviceMerged(MultipleSharedDeviceTestCase):

    @classmethod
    def setup_class(cls):
        cls.drivers, cls.loop = create_shared_drivers(1)
        cls.sign_in = SignInView(cls.drivers[0])
        cls.password = basic_user['special_chars_password']

        cls.home = cls.sign_in.create_user(password=cls.password)
        cls.public_chat_name = cls.home.get_random_chat_name()
        cls.chat = cls.home.join_public_chat(cls.public_chat_name)
        cls.home.home_button.double_click()

    @marks.testrail_id(0000)
    @marks.critical
    def test_onboarding_home_initial_popup(self):
        texts = ["chat-and-transact", "invite-friends"]
        for text in texts:
            if not self.home.element_by_translation_id(text).is_element_displayed():
                self.errors.append("'%s' text is not shown" % self.get_translation_by_key(text))
        if self.home.element_by_text(texts[0]).is_element_displayed():
            self.errors.append("'%s' text is shown, but welcome view was closed" % texts[0])
        self.home.relogin(password=self.password)
        if self.home.element_by_text(texts[0]).is_element_displayed():
            self.errors.append("'%s' text is shown after relogin, but welcome view was closed" % texts[0])
        # if not self.home.element_by_translation_id("welcome-blank-message").is_element_displayed():
        #     self.errors.append("'%s' text is not shown after welcome view was closed" %  self.home.get_translation_by_key(
        #         "welcome-blank-message"))
        self.errors.verify_no_errors()

    @marks.testrail_id(0000)
    @marks.critical
    def test_onboarding_can_share_wallet_address(self):

        self.home.just_fyi("Copying wallet address")
        wallet = self.home.wallet_button.click()
        wallet.accounts_status_account.click()
        request = wallet.receive_transaction_button.click()
        address = wallet.address_text.text
        request.share_button.click()
        request.element_by_translation_id("sharing-copy-to-clipboard").click()

        self.home.just_fyi("Sharing wallet address via messenger")
        request.share_button.click()
        wallet.share_via_messenger()
        if not wallet.element_by_text_part(address).is_element_present():
            self.errors.append("Can't share address")
        wallet.click_system_back_button()

        self.home.just_fyi("Check that can paste wallet address in chat message input")
        wallet.home_button.click()
        self.home.get_chat('#%s' % self.public_chat_name).click()
        self.chat.chat_message_input.click()
        self.chat.paste_text()
        if self.chat.chat_message_input.text != address:
            self.errors.append('Wallet address was not copied')
        self.chat.chat_message_input.clear()
        self.errors.verify_no_errors()

    @marks.testrail_id(0000)
    @marks.critical
    def test_onboarding_can_share_contact_address(self):
        self.home.home_button.double_click()
        self.profile = self.home.profile_button.click()

        self.home.just_fyi("Copying contact code")
        self.profile.share_my_profile_button.click()
        public_key = self.profile.public_key_text.text
        self.profile.public_key_text.long_press_element()
        self.profile.copy_text()

        self.home.just_fyi("Sharing contact code via messenger")
        self.profile.share_button.click()
        self.profile.share_via_messenger()
        if not self.profile.element_by_text_part(public_key).is_element_present():
            self.errors.append("Can't share public key")
        self.profile.click_system_back_button()

        self.home.just_fyi("Check that can paste contact code in chat message input")
        home = self.profile.home_button.click()
        chat = home.add_contact(transaction_senders['M']['public_key'])
        chat.chat_message_input.click()
        chat.paste_text()
        input_text = chat.chat_message_input.text
        if input_text not in public_key or len(input_text) < 1:
            self.errors.append('Public key was not copied')
        chat.chat_message_input.clear()
        self.errors.verify_no_errors()

    @marks.testrail_id(00000)
    @marks.critical
    def test_onboarding_backup_seed_phrase_logcat(self):
        self.home.just_fyi("Check that badge on profile about back up seed phrase is presented")
        if self.home.profile_button.counter.text != '1':
            self.errors.append('Profile button counter is not shown')

        self.home.just_fyi("Back up seed phrase and check logcat")
        profile = self.home.profile_button.click()
        profile.privacy_and_security_button.click()
        profile.backup_recovery_phrase_button.click()
        profile.ok_continue_button.click()
        recovery_phrase = profile.get_recovery_phrase()
        profile.next_button.click()
        word_number = profile.recovery_phrase_word_number.number
        profile.recovery_phrase_word_input.set_value(recovery_phrase[word_number])
        profile.next_button.click()
        word_number_1 = profile.recovery_phrase_word_number.number
        profile.recovery_phrase_word_input.set_value(recovery_phrase[word_number_1])
        profile.done_button.click()
        profile.yes_button.click()
        profile.ok_got_it_button.click()
        if self.home.profile_button.counter.is_element_displayed():
            self.errors.append('Profile button counter is shown after recovery phrase backup')
        values_in_logcat = profile.find_values_in_logcat(passphrase1=recovery_phrase[word_number],
                                                         passphrase2=recovery_phrase[word_number_1])
        if len(values_in_logcat) == 2:
            self.driver.fail(values_in_logcat)
        profile.profile_button.double_click()

        self.home.just_fyi(
            "Try to restore same account from seed phrase (should be possible only to unlock existing account)")
        self.profile.logout()
        self.sign_in.back_button.click()
        self.sign_in.access_key_button.click()
        self.sign_in.enter_seed_phrase_button.click()
        self.sign_in.seedphrase_input.click()
        self.sign_in.seedphrase_input.set_value(' '.join(recovery_phrase.values()))
        self.sign_in.next_button.click()
        self.sign_in.element_by_translation_id(translation_id="unlock", uppercase=True).click()
        self.sign_in.password_input.set_value(common_password)
        self.home.plus_button.click()
        if not self.home.start_new_chat_button.is_element_displayed():
            self.errors.append("Can't proceed using account after it's re-recover twice.")
        self.errors.verify_no_errors()





class TestCreateAccount(SingleDeviceTestCase):


    @marks.testrail_id(5356)
    @marks.critical
    def test_switch_users_special_char_password_and_add_new_account_logcat(self):
        sign_in = SignInView(self.driver)

        sign_in.just_fyi("Creating multiaccount with special char password")
        password = basic_user['special_chars_password']
        home = sign_in.create_user(password=password)
        public_key, default_username = home.get_public_key_and_username(return_username=True)
        profile = home.get_profile_view()
        profile.logout()

        sign_in.just_fyi('Check that cannot login with incorrect password, and can login with valid data')
        if sign_in.ok_button.is_element_displayed():
            sign_in.ok_button.click()
        sign_in.multi_account_on_login_button.click()
        sign_in.password_input.set_value(common_password)
        sign_in.sign_in_button.click()
        sign_in.element_by_translation_id("wrong-password").wait_for_visibility_of_element(20)
        if not sign_in.element_by_text(default_username).is_element_displayed():
            self.driver.fail('Username is not shown while login')
        sign_in.password_input.set_value(password)
        sign_in.sign_in_button.click()
        if not sign_in.home_button.is_element_displayed(10):
            self.driver.fail('User is not logged in')
        values_in_logcat = sign_in.find_values_in_logcat(password=password)
        if values_in_logcat:
            self.driver.fail(values_in_logcat)
        sign_in.profile_button.click()
        profile.logout()

        sign_in.just_fyi('Create another multiaccount')
        if sign_in.ok_button.is_element_displayed():
            sign_in.ok_button.click()
        sign_in.back_button.click()
        sign_in.your_keys_more_icon.click()
        sign_in.generate_new_key_button.click()
        sign_in.next_button.click()
        sign_in.next_button.click()
        sign_in.create_password_input.set_value(common_password)
        sign_in.next_button.click()
        sign_in.confirm_your_password_input.set_value(common_password)
        sign_in.next_button.click()
        sign_in.maybe_later_button.click_until_presence_of_element(sign_in.lets_go_button)
        sign_in.lets_go_button.click()
        if sign_in.get_public_key_and_username() == public_key:
            self.driver.fail('New account was not created')

    @marks.testrail_id(5379)
    @marks.critical
    def test_home_view(self):
        sign_in = SignInView(self.driver)
        sign_in.get_started_button.click()
        if sign_in.generate_key_button.is_element_displayed():
            self.errors.append("Agree with ToS is not mandatory to proceed onboarding!")
        sign_in.accept_tos_checkbox.enable()
        sign_in.get_started_button.click_until_presence_of_element(sign_in.generate_key_button)
        sign_in.generate_key_button.click()
        from views.sign_in_view import MultiAccountButton
        account_button = sign_in.get_multiaccount_by_position(position=random.randint(1, 4),
                                                              element_class=MultiAccountButton)
        pub_chat = 'status'
        username = account_button.username.text
        account_button.click()
        sign_in.next_button.click()
        sign_in.next_button.click()
        sign_in.create_password_input.set_value(common_password)
        sign_in.confirm_your_password_input.set_value(common_password)
        sign_in.next_button.click()
        [element.wait_and_click(10) for element in (sign_in.maybe_later_button, sign_in.lets_go_button)]
        home = sign_in.get_home_view()
        # texts = ["chat-and-transact", "invite-friends"]
        # for text in texts:
        #     if not home.element_by_translation_id(text).is_element_displayed():
        #         self.errors.append("'%s' text is not shown" % self.get_translation_by_key(text))
        home.join_public_chat(pub_chat)
        profile = home.profile_button.click()
        shown_username = profile.default_username_text.text
        if shown_username != username:
            self.errors.append("Default username '%s' doesn't match '%s'" % (shown_username, username))
        profile.home_button.double_click()
        home.cross_icon_inside_welcome_screen_button.click()
        home.delete_chat_long_press('#%s' % pub_chat)
        # if home.element_by_text(texts[0]).is_element_displayed():
        #     self.errors.append("'%s' text is shown, but welcome view was closed" % texts[0])
        # home.relogin()
        # if home.element_by_text(texts[0]).is_element_displayed():
        #     self.errors.append("'%s' text is shown after relogin, but welcome view was closed" % texts[0])
        # if not home.element_by_translation_id("welcome-blank-message").is_element_displayed():
        #     self.errors.append("'%s' text is not shown after welcome view was closed" % home.get_translation_by_key(
        #         "welcome-blank-message"))

        self.errors.verify_no_errors()

    @marks.testrail_id(5394)
    @marks.high
    def test_account_recovery_with_uppercase_whitespaces_seed_phrase_special_char_passw_logcat(self):
        user = transaction_senders['A']
        passphrase = user['passphrase']
        password = basic_user['special_chars_password']
        passphrase = fill_string_with_char(passphrase.upper(), ' ', 3, True, True)
        sign_in = SignInView(self.driver)

        sign_in.just_fyi(
            "Restore multiaccount from uppercase seed phrase with whitespaces and set password with special chars")
        sign_in.recover_access(passphrase, password=password)
        profile = sign_in.profile_button.click()
        username = profile.default_username_text.text
        public_key = sign_in.get_public_key_and_username()

        sign_in.just_fyi("Check public key matches expected and no back up seed phrase is available")
        profile.privacy_and_security_button.click()
        profile.backup_recovery_phrase_button.click()
        if not profile.backup_recovery_phrase_button.is_element_displayed():
            self.errors.append('Back up seed phrase option is active for recovered account!')
        if username != user['username'] or public_key != user['public_key']:
            self.driver.fail('Incorrect user was recovered')
        values_in_logcat = sign_in.find_values_in_logcat(passphrase=passphrase, password=password)
        if values_in_logcat:
            self.driver.fail(values_in_logcat)
        profile.profile_button.double_click()

        sign_in.just_fyi("Check relogin with special char password")
        sign_in.relogin(password=basic_user['special_chars_password'])
        self.errors.verify_no_errors()

    @marks.testrail_id(5363)
    @marks.high
    def test_pass_phrase_validation(self):
        sign_in = SignInView(self.driver)
        sign_in.accept_tos_checkbox.enable()
        sign_in.get_started_button.click_until_presence_of_element(sign_in.access_key_button)
        sign_in.access_key_button.click()
        validations = [
            {
                'case': 'empty value',
                'phrase': '    ',
                'validation message': 'Required field',
                'words count': 1,
                'popup': False
            },
            {
                'case': '1 word seed',
                'phrase': 'a',
                'validation message': '',
                'words count': 1,
                'popup': False
            },
            {
                'case': 'mnemonic but checksum validation fails',
                'phrase': 'one two three four five six seven eight nine ten eleven twelve',
                'validation message': '',
                'words count': 12,
                'popup': True
            },
        ]

        sign_in.just_fyi("check that seed phrase is required (can't be empty)")
        sign_in.enter_seed_phrase_button.click()
        sign_in.next_button.click()
        if sign_in.element_by_translation_id('keycard-recovery-success-header').is_element_displayed():
            self.errors.append("Possible to create account with empty seed phrase")
        for validation in validations:
            sign_in.just_fyi("Checking %s" % validation.get('case'))
            phrase, msg, words_count, popup = validation.get('phrase'), \
                                              validation.get('validation message'), \
                                              validation.get('words count'), \
                                              validation.get('popup')
            if sign_in.access_key_button.is_element_displayed():
                sign_in.access_key_button.click()
            if sign_in.enter_seed_phrase_button.is_element_displayed():
                sign_in.enter_seed_phrase_button.click()

            sign_in.seedphrase_input.set_value(phrase)

            if msg:
                if not sign_in.element_by_text(msg).is_element_displayed():
                    self.errors.append('"{}" message is not shown'.format(msg))

            sign_in.just_fyi('check that words count is shown')
            if words_count:
                if not sign_in.element_by_text('%s word' % words_count):
                    self.errors.append('"%s word" is not shown ' % words_count)
            else:
                if not sign_in.element_by_text('%s words' % words_count):
                    self.errors.append('"%s words" is not shown ' % words_count)

            sign_in.just_fyi('check that "Next" is disabled unless we use allowed count of words')
            if words_count != 12 or 15 or 18 or 21 or 24:
                sign_in.next_button.click()
                if sign_in.element_by_translation_id('keycard-recovery-success-header').is_element_displayed():
                    self.errors.append("Possible to create account with wrong count (%s) of words" % words_count)

            sign_in.just_fyi('check behavior for popup "Custom seed phrase"')
            if popup:

                if not sign_in.custom_seed_phrase_label.is_element_displayed():
                    self.errors.append("Popup about custom seed phrase is not shown")
                sign_in.cancel_custom_seed_phrase_button.click()

            sign_in.click_system_back_button()

        self.errors.verify_no_errors()

    @marks.testrail_id(5335)
    @marks.high
    def test_wallet_set_up(self):
        sign_in = SignInView(self.driver)
        sign_in.recover_access(transaction_senders['A']['passphrase'])
        wallet = sign_in.wallet_button.click()

        wallet.just_fyi("Initiating some transaction so the wallet signing phrase pop-up appears")
        wallet.accounts_status_account.click()
        send_transaction_view = wallet.send_transaction_button.click()
        send_transaction_view.amount_edit_box.click()
        send_transaction_view.amount_edit_box.set_value("0")
        send_transaction_view.set_recipient_address("0x" + transaction_senders['A']['address'])
        send_transaction_view.sign_transaction_button.click()

        texts = list(map(sign_in.get_translation_by_key,
                         ["this-is-you-signing", "three-words-description", "three-words-description-2"]))
        wallet.just_fyi('Check tests in set up wallet popup')
        for text in texts:
            if not wallet.element_by_text_part(text).is_element_displayed():
                self.errors.append("'%s' text is not displayed" % text)
        phrase = wallet.sign_in_phrase.list
        if len(phrase) != 3:
            self.errors.append('Transaction phrase length is %s' % len(phrase))

        wallet.just_fyi('Check popup will reappear if tap on "Remind me later"')
        wallet.remind_me_later_button.click()
        send_transaction_view.cancel_button.click()
        wallet.wallet_button.click()
        wallet.accounts_status_account.click()
        send_transaction = wallet.send_transaction_button.click()
        send_transaction.amount_edit_box.set_value('0')
        send_transaction.set_recipient_address('0x%s' % basic_user['address'])
        send_transaction.next_button.click_until_presence_of_element(send_transaction.sign_transaction_button)
        send_transaction.sign_transaction_button.click()
        for text in texts:
            if not wallet.element_by_text_part(text).is_element_displayed():
                self.errors.append("'%s' text is not displayed" % text)
        phrase_1 = wallet.sign_in_phrase.list
        if phrase_1 != phrase:
            self.errors.append("Transaction phrase '%s' doesn't match expected '%s'" % (phrase_1, phrase))
        wallet.ok_got_it_button.click()
        wallet.cancel_button.click()
        wallet.home_button.click()
        wallet.wallet_button.click()
        for text in texts:
            if wallet.element_by_text_part(text).is_element_displayed():
                self.errors.append('Signing phrase pop up appears after wallet set up')
                break
        self.errors.verify_no_errors()

    @marks.critical
    @marks.testrail_id(5419)
    @marks.flaky
    def test_logcat_backup_recovery_phrase(self):
        sign_in = SignInView(self.driver)
        home = sign_in.create_user()

        # home.just_fyi("Check that badge on profile about back up seed phrase is presented")
        # if home.profile_button.counter.text != '1':
        #     self.errors.append('Profile button counter is not shown')
        #
        # home.just_fyi("Back up seed phrase and check logcat")
        # profile = home.profile_button.click()
        # profile.privacy_and_security_button.click()
        # profile.backup_recovery_phrase_button.click()
        # profile.ok_continue_button.click()
        # recovery_phrase = profile.get_recovery_phrase()
        # profile.next_button.click()
        # word_number = profile.recovery_phrase_word_number.number
        # profile.recovery_phrase_word_input.set_value(recovery_phrase[word_number])
        # profile.next_button.click()
        # word_number_1 = profile.recovery_phrase_word_number.number
        # profile.recovery_phrase_word_input.set_value(recovery_phrase[word_number_1])
        # profile.done_button.click()
        # profile.yes_button.click()
        # profile.ok_got_it_button.click()
        # if home.profile_button.counter.is_element_displayed():
        #     self.errors.append('Profile button counter is shown after recovery phrase backup')
        # values_in_logcat = profile.find_values_in_logcat(passphrase1=recovery_phrase[word_number],
        #                                                  passphrase2=recovery_phrase[word_number_1])
        # if len(values_in_logcat) == 2:
        #     self.driver.fail(values_in_logcat)
        # profile.profile_button.double_click()
        #
        # home.just_fyi(
        #     "Try to restore same account from seed phrase (should be possible only to unlock existing account)")
        # profile.logout()
        # sign_in.back_button.click()
        # sign_in.access_key_button.click()
        # sign_in.enter_seed_phrase_button.click()
        # sign_in.seedphrase_input.click()
        # sign_in.seedphrase_input.set_value(' '.join(recovery_phrase.values()))
        # sign_in.next_button.click()
        # sign_in.element_by_translation_id(translation_id="unlock", uppercase=True).click()
        # sign_in.password_input.set_value(common_password)
        # chat = sign_in.sign_in_button.click()
        # chat.plus_button.click()
        # if not chat.start_new_chat_button.is_element_displayed():
        #     self.errors.append("Can't proceed using account after it's re-recover twice.")
        self.errors.verify_no_errors()

    @marks.testrail_id(6296)
    @marks.high
    def test_recover_account_from_new_user_seedphrase(self):
        home = SignInView(self.driver).create_user()
        profile = home.profile_button.click()
        profile.privacy_and_security_button.click()
        profile.backup_recovery_phrase_button.click()
        profile.ok_continue_button.click()
        recovery_phrase = " ".join(profile.get_recovery_phrase().values())
        profile.close_button.click()
        profile.back_button.click()
        public_key = profile.get_public_key_and_username()
        wallet = profile.wallet_button.click()
        address = wallet.get_wallet_address()
        home.profile_button.click()
        profile.logout()
        self.driver.reset()
        SignInView(self.driver).recover_access(recovery_phrase)
        wallet = home.wallet_button.click()
        if wallet.get_wallet_address() != address:
            self.driver.fail("Seed phrase displayed in new accounts for back up does not recover respective address")
        profile = wallet.profile_button.click()
        if profile.get_public_key_and_username() != public_key:
            self.driver.fail("Seed phrase displayed in new accounts for back up does not recover respective public key")

    # @marks.testrail_id(5323)
    # @marks.critical
    # def test_share_copy_contact_code_and_wallet_address(self):
    #     home = SignInView(self.driver).create_user()
        # profile = home.profile_button.click()
        #
        # home.just_fyi("Copying contact code")
        # profile.share_my_profile_button.click()
        # public_key = profile.public_key_text.text
        # profile.public_key_text.long_press_element()
        # profile.copy_text()
        #
        # home.just_fyi("Sharing contact code via messenger")
        # profile.share_button.click()
        # profile.share_via_messenger()
        # if not profile.element_by_text_part(public_key).is_element_present():
        #     self.errors.append("Can't share public key")
        # profile.click_system_back_button()
        #
        # home.just_fyi("Check that can paste contact code in chat message input")
        # home = profile.home_button.click()
        # chat = home.add_contact(transaction_senders['M']['public_key'])
        # chat.chat_message_input.click()
        # chat.paste_text()
        # input_text = chat.chat_message_input.text
        # if input_text not in public_key or len(input_text) < 1:
        #     self.errors.append('Public key was not copied')
        # chat.chat_message_input.clear()
        # chat.home_button.click()

        # home.just_fyi("Copying wallet address")
        # wallet = profile.wallet_button.click()
        # wallet.accounts_status_account.click()
        # request = wallet.receive_transaction_button.click()
        # address = wallet.address_text.text
        # request.share_button.click()
        # request.element_by_translation_id("sharing-copy-to-clipboard").click()
        #
        # home.just_fyi("Sharing wallet address via messenger")
        # request.share_button.click()
        # wallet.share_via_messenger()
        # if not wallet.element_by_text_part(address).is_element_present():
        #     self.errors.append("Can't share address")
        # wallet.click_system_back_button()
        #
        # home.just_fyi("Check that can paste wallet address in chat message input")
        # wallet.home_button.click()
        # home.get_chat(transaction_senders['M']['username']).click()
        # chat.chat_message_input.click()
        # chat.paste_text()
        # if chat.chat_message_input.text != address:
        #     self.errors.append('Wallet address was not copied')
        # self.errors.verify_no_errors()

    # @marks.testrail_id(5460)
    # @marks.medium
    # def test_create_account_short_and_mismatch_password(self):
    #     sign_in = SignInView(self.driver)
    #     sign_in.accept_tos_checkbox.enable()
    #     sign_in.get_started_button.click()
    #     sign_in.generate_key_button.click()
    #     sign_in.next_button.click()
    #     sign_in.next_button.click()
    #     cases = ['password is not confirmed', 'password is too short', "passwords don't match"]
    #     error = "Can create multiaccount when"
    #
    #     sign_in.just_fyi('Checking case when %s' % cases[0])
    #     sign_in.create_password_input.send_keys('123456')
    #     sign_in.next_button.click()
    #     if sign_in.maybe_later_button.is_element_displayed(10):
    #         self.driver.fail('%s  %s' % (error, cases[0]))
    #
    #     sign_in.just_fyi('Checking case when %s' % cases[1])
    #     sign_in.create_password_input.send_keys('123456')
    #     [field.send_keys('123456') for field in (sign_in.create_password_input, sign_in.confirm_your_password_input)]
    #     sign_in.confirm_your_password_input.delete_last_symbols(1)
    #     sign_in.create_password_input.delete_last_symbols(1)
    #     sign_in.next_button.click()
    #     if sign_in.maybe_later_button.is_element_displayed(10):
    #         self.driver.fail('%s  %s' % (error, cases[1]))
    #
    #     sign_in.just_fyi("Checking case %s" % cases[2])
    #     sign_in.create_password_input.send_keys('1234565')
    #     sign_in.confirm_your_password_input.send_keys('1234567')
    #     if not sign_in.element_by_translation_id("password_error1").is_element_displayed():
    #         self.errors.append("'%s' is not shown" % sign_in.get_translation_by_key("password_error1"))
    #     sign_in.next_button.click()
    #     if sign_in.maybe_later_button.is_element_displayed(10):
    #         self.driver.fail('%s  %s' % (error, cases[2]))
    #
    #     self.errors.verify_no_errors()
    #
    # @marks.testrail_id(5455)
    # @marks.medium
    # def test_recover_accounts_with_certain_seedphrase(self):
    #     sign_in = SignInView(self.driver)
    #     for phrase, account in recovery_users.items():
    #         home_view = sign_in.recover_access(passphrase=phrase, password=unique_password)
    #         wallet_view = home_view.wallet_button.click()
    #         address = wallet_view.get_wallet_address()
    #         if address != account:
    #             self.errors.append('Restored wallet address "%s" does not match expected "%s"' % (address, account))
    #         profile = home_view.profile_button.click()
    #         profile.privacy_and_security_button.click()
    #         profile.delete_my_profile_button.scroll_and_click()
    #         profile.delete_my_profile_password_input.set_value(unique_password)
    #         profile.delete_profile_button.click()
    #         profile.ok_button.click()
    #     self.errors.verify_no_errors()
