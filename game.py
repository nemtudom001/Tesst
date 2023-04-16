import os
import app
import dbg
import grp
import item
import background
import chr
import chrmgr
import player
import snd
import chat
import textTail
import snd
import net
import effect
import wndMgr
import fly
import systemSetting
import quest
import guild
import skill
import messenger
import localeInfo
import constInfo
import exchange
import ime

import ui
import uiCommon
import uiPhaseCurtain
import uiMapNameShower
import uiAffectShower
import uiPlayerGauge
import uiCharacter
import uiTarget
import sys

import event
import time
#import constInfo2

# PRIVATE_SHOP_PRICE_LIST
import uiPrivateShopBuilder
# END_OF_PRIVATE_SHOP_PRICE_LIST

import mouseModule
import consoleModule

import playerSettingModule
import interfaceModule

import musicInfo
import uiPetSystem
import stringCommander

from _weakref import proxy

if app.USE_INGAME_WIKI and False:
	import mb_ingameWiki


####Mijago switch
from switchbot import Bot
######################


# TEXTTAIL_LIVINGTIME_CONTROL
#if localeInfo.IsJAPAN():
#	app.SetTextTailLivingTime(8.0)
# END_OF_TEXTTAIL_LIVINGTIME_CONTROL

# SCREENSHOT_CWDSAVE
SCREENSHOT_CWDSAVE = False
SCREENSHOT_DIR = None

if localeInfo.IsEUROPE():
	SCREENSHOT_CWDSAVE = True

if localeInfo.IsCIBN10():
	SCREENSHOT_CWDSAVE = False
	SCREENSHOT_DIR = "YT2W"

cameraDistance = 1550.0
cameraPitch = 27.0
cameraRotation = 0.0
cameraHeight = 100.0
#pet_gui_activado = 0

testAlignment = 0
BPisLodaded = 0

_debug=lambda msg,func=sys.stderr.write:__DEBUG__ and func("| %s | "%str(msg))or(None)

class GameWindow(ui.ScriptWindow):
	def __init__(self, stream):
		ui.ScriptWindow.__init__(self, "GAME")
		self.SetWindowName("game")
		net.SetPhaseWindow(net.PHASE_WINDOW_GAME, self)
		player.SetGameWindow(self)
		
		####Mijago Switch
		self.switchbot = Bot()
		self.switchbot.Hide()
		#####################
		
		localeInfo.SEND_BACK = ""
		
		#self.__MakeRain()

		self.quickSlotPageIndex = 0
		self.lastPKModeSendedTime = 0
		self.pressNumber = None

		self.guildWarQuestionDialog = None
		self.interface = None
		self.targetBoard = None
		self.console = None
		self.mapNameShower = None
		self.affectShower = None
		self.playerGauge = None	
		self.petInventoryWnd = None
		
		#self.GiftBox = ui.Button()
		#self.GiftBox.SetUpVisual("d:/ymir work/ui/present.tga")
		#self.GiftBox.SetOverVisual("d:/ymir work/ui/present.tga")
		#self.GiftBox.SetDownVisual("d:/ymir work/ui/present.tga")
		#self.GiftBox.SetText(" ")
		#self.GiftBox.SetToolTipText("Napi ajándék!")
		#self.GiftBox.SetPosition(10, int(wndMgr.GetScreenHeight())-140)
		#self.GiftBox.SetEvent(self.ZetsuGiftSystem__deff__)
		#self.GiftBox.Show()		

		self.stream=stream
		self.interface = interfaceModule.Interface()
		self.interface.MakeInterface()
		self.interface.ShowDefaultWindows()

		self.curtain = uiPhaseCurtain.PhaseCurtain()
		self.curtain.speed = 0.03
		self.curtain.Hide()

		self.targetBoard = uiTarget.TargetBoard()
		self.targetBoard.SetWhisperEvent(ui.__mem_func__(self.interface.OpenWhisperDialog))
		self.targetBoard.Hide()
		
		self.petmain = uiPetSystem.PetSystemMain()
		self.petmini = uiPetSystem.PetSystemMini()		

		self.console = consoleModule.ConsoleWindow()
		self.console.BindGameClass(self)
		self.console.SetConsoleSize(wndMgr.GetScreenWidth(), 200)
		self.console.Hide()

		self.mapNameShower = uiMapNameShower.MapNameShower()
		self.affectShower = uiAffectShower.AffectShower(self.interface)

		self.playerGauge = uiPlayerGauge.PlayerGauge(self)
		self.playerGauge.Hide()
		
		#wj 2014.1.2. ESC?? ?? ? ????? DropQuestionDialog? ??? ????. ??? ??? itemDropQuestionDialog? ???? ?? ?? ERROR? ???? init?? ??? ??? ??? ??.
		self.itemDropQuestionDialog = None

		self.__SetQuickSlotMode()

		self.__ServerCommand_Build()
		self.__ProcessPreservedServerCommand()

		self.isHideAll = False
		self.saveHideWnds = None
		
		
		#self.timeLine = ui.TextLine()
		#self.timeLine.SetFontName(localeInfo.UI_DEF_FONT )
		#self.timeLine.SetFontColor(1, 1, 1)
		#self.timeLine.SetPosition((wndMgr.GetScreenWidth() - 133) / 2, 150)
			

	def __del__(self):
		player.SetGameWindow(0)
		net.ClearPhaseWindow(net.PHASE_WINDOW_GAME, self)
		ui.ScriptWindow.__del__(self)
		del self.saveHideWnds
		del self.isHideAll

	def Open(self):
		app.SetFrameSkip(1)
    
		self.SetSize(wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())

		self.quickSlotPageIndex = 0
		self.PickingCharacterIndex = -1
		self.PickingItemIndex = -1
		self.consoleEnable = False
		self.isShowDebugInfo = False
		self.ShowNameFlag = False

		self.enableXMasBoom = False
		self.startTimeXMasBoom = 0.0
		self.indexXMasBoom = 0

		global cameraDistance, cameraPitch, cameraRotation, cameraHeight

		app.SetCamera(cameraDistance, cameraPitch, cameraRotation, cameraHeight)

		constInfo.SET_DEFAULT_CAMERA_MAX_DISTANCE()
		constInfo.SET_DEFAULT_CHRNAME_COLOR()
		constInfo.SET_DEFAULT_FOG_LEVEL()
		constInfo.SET_DEFAULT_CONVERT_EMPIRE_LANGUAGE_ENABLE()
		constInfo.SET_DEFAULT_USE_ITEM_WEAPON_TABLE_ATTACK_BONUS()
		constInfo.SET_DEFAULT_USE_SKILL_EFFECT_ENABLE()

		# TWO_HANDED_WEAPON_ATTACK_SPEED_UP
		constInfo.SET_TWO_HANDED_WEAPON_ATT_SPEED_DECREASE_VALUE()
		# END_OF_TWO_HANDED_WEAPON_ATTACK_SPEED_UP

		import event
		event.SetLeftTimeString(localeInfo.UI_LEFT_TIME)

		textTail.EnablePKTitle(constInfo.PVPMODE_ENABLE)

		if constInfo.PVPMODE_TEST_ENABLE:
			self.testPKMode = ui.TextLine()
			self.testPKMode.SetFontName(localeInfo.UI_DEF_FONT)
			self.testPKMode.SetPosition(0, 15)
			self.testPKMode.SetWindowHorizontalAlignCenter()
			self.testPKMode.SetHorizontalAlignCenter()
			self.testPKMode.SetFeather()
			self.testPKMode.SetOutline()
			self.testPKMode.Show()

			self.testAlignment = ui.TextLine()
			self.testAlignment.SetFontName(localeInfo.UI_DEF_FONT)
			self.testAlignment.SetPosition(0, 35)
			self.testAlignment.SetWindowHorizontalAlignCenter()
			self.testAlignment.SetHorizontalAlignCenter()
			self.testAlignment.SetFeather()
			self.testAlignment.SetOutline()
			self.testAlignment.Show()

		self.__BuildKeyDict()
		self.__BuildDebugInfo()

		# PRIVATE_SHOP_PRICE_LIST
		uiPrivateShopBuilder.Clear()
		# END_OF_PRIVATE_SHOP_PRICE_LIST

		# UNKNOWN_UPDATE
		exchange.InitTrading()
		# END_OF_UNKNOWN_UPDATE

		if __DEBUG__:
			self.ToggleDebugInfo()

		## Sound
		snd.SetMusicVolume(systemSetting.GetMusicVolume()*net.GetFieldMusicVolume())
		snd.SetSoundVolume(systemSetting.GetSoundVolume())

		netFieldMusicFileName = net.GetFieldMusicFileName()
		if netFieldMusicFileName:
			snd.FadeInMusic("Data/sound_lib/Sound/" + netFieldMusicFileName)
		elif musicInfo.fieldMusic != "":						
			snd.FadeInMusic("Data/sound_lib/Sound/" + musicInfo.fieldMusic)

		self.__SetQuickSlotMode()
		self.__SelectQuickPage(self.quickSlotPageIndex)

		self.SetFocus()
		self.Show()
		app.ShowCursor()

		net.SendEnterGamePacket()

		# START_GAME_ERROR_EXIT
		try:
			self.StartGame()
		except:
			import exception
			exception.Abort("GameWindow.Open")
		# END_OF_START_GAME_ERROR_EXIT
		
		# NPC? ??????? ?? ? ?? ????? ??? ??
		# ex) cubeInformation[20383] = [ {"rewordVNUM": 72723, "rewordCount": 1, "materialInfo": "101,1&102,2", "price": 999 }, ... ]
		self.cubeInformation = {}
		self.currentCubeNPC = 0

		if app.ENABLE_FOG_FIX:
			if systemSetting.IsFogMode():
				background.SetEnvironmentFog(True)
			else:
				background.SetEnvironmentFog(False)	
				
		if app.USE_INGAME_WIKI and False:
			if mb_ingameWiki:
				self.wndWikiModule = mb_ingameWiki.InGameWiki()
		
		constInfo.savedPos = [-1.0, -1.0, -1]
		
	def Close(self):
		self.Hide()

		global cameraDistance, cameraPitch, cameraRotation, cameraHeight
		(cameraDistance, cameraPitch, cameraRotation, cameraHeight) = app.GetCamera()
			
		if app.USE_INGAME_WIKI and False:
			if mb_ingameWiki and self.wndWikiModule:
				self.wndWikiModule.Close()
				self.wndWikiModule = None
			
		if musicInfo.fieldMusic != "":
			snd.FadeOutMusic("Data/sound_lib/Sound/"+ musicInfo.fieldMusic)

		self.onPressKeyDict = None
		self.onClickKeyDict = None

		chat.Close()	
		
		snd.StopAllSound()
		grp.InitScreenEffect()
		chr.Destroy()
		textTail.Clear()
		quest.Clear()
		background.Destroy()
		guild.Destroy()
		messenger.Destroy()
		skill.ClearSkillData()
		wndMgr.Unlock()
		mouseModule.mouseController.DeattachObject()

		if self.guildWarQuestionDialog:
			self.guildWarQuestionDialog.Close()

		self.guildNameBoard = None
		self.partyRequestQuestionDialog = None
		self.partyInviteQuestionDialog = None
		self.guildInviteQuestionDialog = None
		self.guildWarQuestionDialog = None
		self.messengerAddFriendQuestion = None

		# UNKNOWN_UPDATE
		self.itemDropQuestionDialog = None
		# END_OF_UNKNOWN_UPDATE

		# QUEST_CONFIRM
		self.confirmDialog = None
		# END_OF_QUEST_CONFIRM

		self.PrintCoord = None
		self.FrameRate = None
		self.Pitch = None
		self.Splat = None
		self.TextureNum = None
		self.ObjectNum = None
		self.ViewDistance = None
		self.PrintMousePos = None

		self.ClearDictionary()
		
		self.petmain.Close()
		self.petmini.Close()		

		self.playerGauge = None
		self.mapNameShower = None
		self.affectShower = None

		if self.console:
			self.console.BindGameClass(0)
			self.console.Close()
			self.console=None
		
		if self.targetBoard:
			self.targetBoard.Destroy()
			self.targetBoard = None
	
		if self.interface:
			self.interface.HideAllWindows()
			self.interface.Close()
			self.interface=None
			
		if self.petInventoryWnd:
			self.petInventoryWnd.Destroy()
			self.petInventoryWnd = None			

		player.ClearSkillDict()
		player.ResetCameraRotation()

		self.KillFocus()
		app.HideCursor()

		print "---------------------------------------------------------------------------- CLOSE GAME WINDOW"

	def __BuildKeyDict(self):
		onPressKeyDict = {}

		##PressKey ? ??? ?? ?? ?? ???? ???.
		
		## ?? ??? ???? ????.(?? ???? ? ??? ??)
		## F12 ? ?? ???? ???? ?? ?? ? ??.
		onPressKeyDict[app.DIK_1]	= lambda : self.__PressNumKey(1)
		onPressKeyDict[app.DIK_2]	= lambda : self.__PressNumKey(2)
		onPressKeyDict[app.DIK_3]	= lambda : self.__PressNumKey(3)
		onPressKeyDict[app.DIK_4]	= lambda : self.__PressNumKey(4)
		onPressKeyDict[app.DIK_5]	= lambda : self.__PressNumKey(5)
		onPressKeyDict[app.DIK_6]	= lambda : self.__PressNumKey(6)
		onPressKeyDict[app.DIK_7]	= lambda : self.__PressNumKey(7)
		onPressKeyDict[app.DIK_8]	= lambda : self.__PressNumKey(8)
		onPressKeyDict[app.DIK_9]	= lambda : self.__PressNumKey(9)
		onPressKeyDict[app.DIK_F1]	= lambda : self.__PressQuickSlot(5)
		onPressKeyDict[app.DIK_F2]	= lambda : self.__PressQuickSlot(6)
		onPressKeyDict[app.DIK_F3]	= lambda : self.__PressQuickSlot(7)
		onPressKeyDict[app.DIK_F4]	= lambda : self.__PressQuickSlot(8)
		onPressKeyDict[app.DIK_F5]	= lambda : self.__PressQuickSlot(9)
		#onPressKeyDict[app.DIK_F6]	= lambda : self.__Bonuszcserelo()
		#onPressKeyDict[app.DIK_F7]	= lambda : self.__Bonuszcserelo2()   ###Mijago switch
		onPressKeyDict[app.DIK_F8]	= lambda : self.__ToggleWiki()
		#onPressKeyDict[app.DIK_TAB]	= lambda : self.__switch_channel()
		#onPressKeyDict[app.DIK_F11]    = lambda : self.__FortunaAOpenA()
		#onPressKeyDict[app.DIK_F7]    = lambda : self.__Asd()
		#onPressKeyDict[app.DIK_F6]    = lambda : self.__Asd2()

		onPressKeyDict[app.DIK_LALT]		= lambda : self.ShowName()
		onPressKeyDict[app.DIK_LCONTROL]	= lambda : self.ShowMouseImage()
		onPressKeyDict[app.DIK_SYSRQ]		= lambda : self.SaveScreen()
		onPressKeyDict[app.DIK_SPACE]		= lambda : self.StartAttack()

		#??? ???
		onPressKeyDict[app.DIK_UP]			= lambda : self.MoveUp()
		onPressKeyDict[app.DIK_DOWN]		= lambda : self.MoveDown()
		onPressKeyDict[app.DIK_LEFT]		= lambda : self.MoveLeft()
		onPressKeyDict[app.DIK_RIGHT]		= lambda : self.MoveRight()
		onPressKeyDict[app.DIK_W]			= lambda : self.MoveUp()
		onPressKeyDict[app.DIK_S]			= lambda : self.MoveDown()
		onPressKeyDict[app.DIK_A]			= lambda : self.MoveLeft()
		onPressKeyDict[app.DIK_D]			= lambda : self.MoveRight()

		onPressKeyDict[app.DIK_E]			= lambda: app.RotateCamera(app.CAMERA_TO_POSITIVE)
		onPressKeyDict[app.DIK_R]			= lambda: app.ZoomCamera(app.CAMERA_TO_NEGATIVE)
		#onPressKeyDict[app.DIK_F]			= lambda: app.ZoomCamera(app.CAMERA_TO_POSITIVE)
		onPressKeyDict[app.DIK_T]			= lambda: app.PitchCamera(app.CAMERA_TO_NEGATIVE)
		onPressKeyDict[app.DIK_G]			= self.__PressGKey
		onPressKeyDict[app.DIK_Q]			= self.__PressQKey
		onPressKeyDict[app.DIK_P]			= self.__PressPKey

		onPressKeyDict[app.DIK_NUMPAD9]		= lambda: app.MovieResetCamera()
		onPressKeyDict[app.DIK_NUMPAD4]		= lambda: app.MovieRotateCamera(app.CAMERA_TO_NEGATIVE)
		onPressKeyDict[app.DIK_NUMPAD6]		= lambda: app.MovieRotateCamera(app.CAMERA_TO_POSITIVE)
		onPressKeyDict[app.DIK_PGUP]		= lambda: app.MovieZoomCamera(app.CAMERA_TO_NEGATIVE)
		onPressKeyDict[app.DIK_PGDN]		= lambda: app.MovieZoomCamera(app.CAMERA_TO_POSITIVE)
		onPressKeyDict[app.DIK_NUMPAD8]		= lambda: app.MoviePitchCamera(app.CAMERA_TO_NEGATIVE)
		onPressKeyDict[app.DIK_NUMPAD2]		= lambda: app.MoviePitchCamera(app.CAMERA_TO_POSITIVE)
		onPressKeyDict[app.DIK_GRAVE]		= lambda : self.PickUpItem()
		onPressKeyDict[app.DIK_Z]			= lambda : self.PickUpItem()
		onPressKeyDict[app.DIK_C]			= lambda state = "STATUS": self.interface.ToggleCharacterWindow(state)
		onPressKeyDict[app.DIK_V]			= lambda state = "SKILL": self.interface.ToggleCharacterWindow(state)
		#onPressKeyDict[app.DIK_B]			= lambda state = "EMOTICON": self.interface.ToggleCharacterWindow(state)
		onPressKeyDict[app.DIK_N]			= lambda state = "QUEST": self.interface.ToggleCharacterWindow(state)
		onPressKeyDict[app.DIK_I]			= lambda : self.interface.ToggleInventoryWindow()
		onPressKeyDict[app.DIK_O]			= lambda : self.interface.ToggleDragonSoulWindowWithNoInfo()
		onPressKeyDict[app.DIK_M]			= lambda : self.interface.PressMKey()
		#onPressKeyDict[app.DIK_H]			= lambda : self.interface.OpenHelpWindow()
		onPressKeyDict[app.DIK_ADD]			= lambda : self.interface.MiniMapScaleUp()
		onPressKeyDict[app.DIK_SUBTRACT]	= lambda : self.interface.MiniMapScaleDown()
		onPressKeyDict[app.DIK_L]			= lambda : self.interface.ToggleChatLogWindow()
		onPressKeyDict[app.DIK_COMMA]		= lambda : self.ShowConsole()		# "`" key
		onPressKeyDict[app.DIK_LSHIFT]		= lambda : self.__SetQuickPageMode()

		onPressKeyDict[app.DIK_J]			= lambda : self.__PressJKey()
		onPressKeyDict[app.DIK_H]			= lambda : self.__PressHKey()
		onPressKeyDict[app.DIK_B]			= lambda : self.__PressBKey()
		onPressKeyDict[app.DIK_F]			= lambda : self.__PressFKey()
		if TEST_ENVIROMENT:
			onPressKeyDict[app.DIK_F12]		= lambda : self.ToggleDebugstuff()
			onPressKeyDict[app.DIK_F11]		= lambda : self.ToggleAllWindows()
		#onPressKeyDict[app.DIK_U]			= lambda : self.__PressExtendedInventory()
		# CUBE_TEST
		#onPressKeyDict[app.DIK_K]			= lambda : self.interface.OpenCubeWindow()
		# CUBE_TEST_END
		if app.ENABLE_SPECIAL_STORAGE:
			onPressKeyDict[app.DIK_U]			= lambda : self.interface.ToggleSpecialStorage()

		self.onPressKeyDict = onPressKeyDict

		onClickKeyDict = {}
		onClickKeyDict[app.DIK_UP] = lambda : self.StopUp()
		onClickKeyDict[app.DIK_DOWN] = lambda : self.StopDown()
		onClickKeyDict[app.DIK_LEFT] = lambda : self.StopLeft()
		onClickKeyDict[app.DIK_RIGHT] = lambda : self.StopRight()
		onClickKeyDict[app.DIK_SPACE] = lambda : self.EndAttack()

		onClickKeyDict[app.DIK_W] = lambda : self.StopUp()
		onClickKeyDict[app.DIK_S] = lambda : self.StopDown()
		onClickKeyDict[app.DIK_A] = lambda : self.StopLeft()
		onClickKeyDict[app.DIK_D] = lambda : self.StopRight()
		onClickKeyDict[app.DIK_Q] = lambda: app.RotateCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_E] = lambda: app.RotateCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_R] = lambda: app.ZoomCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_F] = lambda: app.ZoomCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_T] = lambda: app.PitchCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_G] = lambda: self.__ReleaseGKey()
		onClickKeyDict[app.DIK_NUMPAD4] = lambda: app.MovieRotateCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_NUMPAD6] = lambda: app.MovieRotateCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_PGUP] = lambda: app.MovieZoomCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_PGDN] = lambda: app.MovieZoomCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_NUMPAD8] = lambda: app.MoviePitchCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_NUMPAD2] = lambda: app.MoviePitchCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_LALT] = lambda: self.HideName()
		onClickKeyDict[app.DIK_LCONTROL] = lambda: self.HideMouseImage()
		onClickKeyDict[app.DIK_LSHIFT] = lambda: self.__SetQuickSlotMode()
		onClickKeyDict[app.DIK_P] = lambda: self.OpenPetMainGui()

		#if constInfo.PVPMODE_ACCELKEY_ENABLE:
		#	onClickKeyDict[app.DIK_B] = lambda: self.ChangePKMode()

		self.onClickKeyDict=onClickKeyDict
	if app.WJ_SPLIT_INVENTORY_SYSTEM:
		def __PressExtendedInventory(self):
			if self.interface:
				self.interface.ToggleExtendedInventoryWindow()
			
	def __ToggleWiki(self):
		if app.USE_INGAME_WIKI and False:
			if mb_ingameWiki and self.wndWikiModule:
				self.wndWikiModule.Open()
		
	def __PressNumKey(self,num):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			
			if num >= 1 and num <= 9:
				if(chrmgr.IsPossibleEmoticon(-1)):				
					chrmgr.SetEmoticon(-1,int(num)-1)
					net.SendEmoticon(int(num)-1)
		else:
			if num >= 1 and num <= 5:
				self.pressNumber(num-1)

	def __ClickBKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			return
		else:
			if constInfo.PVPMODE_ACCELKEY_ENABLE:
				self.ChangePKMode()


	def	__PressJKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			if player.IsMountingHorse():
				net.SendChatPacket("/unmount")
			else:
				#net.SendChatPacket("/user_horse_ride")
				if not uiPrivateShopBuilder.IsBuildingPrivateShop():
					for i in xrange(player.INVENTORY_PAGE_SIZE):
						if player.GetItemIndex(i) in (71114, 71116, 71118, 71120):
							net.SendItemUsePacket(i)
							break
	def	__PressHKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			net.SendChatPacket("/user_horse_ride")
		else:
			self.interface.OpenHelpWindow()

	def	__PressBKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			net.SendChatPacket("/user_horse_back")
		else:
			state = "EMOTICON"
			self.interface.ToggleCharacterWindow(state)

	def	__PressFKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			net.SendChatPacket("/user_horse_feed")	
		else:
			app.ZoomCamera(app.CAMERA_TO_POSITIVE)

	def __PressGKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			net.SendChatPacket("/ride")	
		else:
			if self.ShowNameFlag:
				self.interface.ToggleGuildWindow()
			else:
				app.PitchCamera(app.CAMERA_TO_POSITIVE)

	def	__ReleaseGKey(self):
		app.PitchCamera(app.CAMERA_STOP)

	def __PressQKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			if 0==interfaceModule.IsQBHide:
				interfaceModule.IsQBHide = 1
				self.interface.HideAllQuestButton()
			else:
				interfaceModule.IsQBHide = 0
				self.interface.ShowAllQuestButton()
		else:
			app.RotateCamera(app.CAMERA_TO_NEGATIVE)
			
	def __PressPKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			if 0==interfaceModule.IsWisperHide:
				interfaceModule.IsWisperHide = 1
				self.interface.HideAllWhisperButton()
			else:
				interfaceModule.IsWisperHide= 0
				self.interface.ShowAllWhisperButton()		

	def __SetQuickSlotMode(self):
		self.pressNumber=ui.__mem_func__(self.__PressQuickSlot)

	def __SetQuickPageMode(self):
		self.pressNumber=ui.__mem_func__(self.__SelectQuickPage)

	def __PressQuickSlot(self, localSlotIndex):
		if localeInfo.IsARABIC():
			if 0 <= localSlotIndex and localSlotIndex < 4:
				player.RequestUseLocalQuickSlot(3-localSlotIndex)
			else:
				player.RequestUseLocalQuickSlot(11-localSlotIndex)
		else:
			player.RequestUseLocalQuickSlot(localSlotIndex)	

	def __SelectQuickPage(self, pageIndex):
		self.quickSlotPageIndex = pageIndex
		player.SetQuickPage(pageIndex)

	def ToggleDebugInfo(self):
		self.isShowDebugInfo = not self.isShowDebugInfo

		if self.isShowDebugInfo:
			self.PrintCoord.Show()
			self.FrameRate.Show()
			self.Pitch.Show()
			self.Splat.Show()
			self.TextureNum.Show()
			self.ObjectNum.Show()
			self.ViewDistance.Show()
			self.PrintMousePos.Show()
		else:
			self.PrintCoord.Hide()
			self.FrameRate.Hide()
			self.Pitch.Hide()
			self.Splat.Hide()
			self.TextureNum.Hide()
			self.ObjectNum.Hide()
			self.ViewDistance.Hide()
			self.PrintMousePos.Hide()

	def ToggleDebugstuff(self):
		if not app.IsPressed(app.DIK_LCONTROL):
			app.ToggleCollisionRender()
		else:
			app.ToggleRenderOptimisation()

	def ToggleAllWindows(self):
		if not self.isHideAll:
			self.saveHideWnds = self.interface.ToggleAllWindows()
			self.affectShower.Hide()
			self.isHideAll = True
		else:
			self.interface.ToggleAllWindows(self.saveHideWnds)
			self.affectShower.Show()
			self.isHideAll = False
			self.saveHideWnds = None

	def __BuildDebugInfo(self):
		## Character Position Coordinate
		self.PrintCoord = ui.TextLine()
		self.PrintCoord.SetFontName(localeInfo.UI_DEF_FONT)
		self.PrintCoord.SetPosition(wndMgr.GetScreenWidth() - 270, 0)
		
		## Frame Rate
		self.FrameRate = ui.TextLine()
		self.FrameRate.SetFontName(localeInfo.UI_DEF_FONT)
		self.FrameRate.SetPosition(wndMgr.GetScreenWidth() - 270, 20)

		## Camera Pitch
		self.Pitch = ui.TextLine()
		self.Pitch.SetFontName(localeInfo.UI_DEF_FONT)
		self.Pitch.SetPosition(wndMgr.GetScreenWidth() - 270, 40)

		## Splat
		self.Splat = ui.TextLine()
		self.Splat.SetFontName(localeInfo.UI_DEF_FONT)
		self.Splat.SetPosition(wndMgr.GetScreenWidth() - 270, 60)
		
		##
		self.PrintMousePos = ui.TextLine()
		self.PrintMousePos.SetFontName(localeInfo.UI_DEF_FONT)
		self.PrintMousePos.SetPosition(wndMgr.GetScreenWidth() - 270, 80)

		# TextureNum
		self.TextureNum = ui.TextLine()
		self.TextureNum.SetFontName(localeInfo.UI_DEF_FONT)
		self.TextureNum.SetPosition(wndMgr.GetScreenWidth() - 270, 100)

		# ???? ??? ??
		self.ObjectNum = ui.TextLine()
		self.ObjectNum.SetFontName(localeInfo.UI_DEF_FONT)
		self.ObjectNum.SetPosition(wndMgr.GetScreenWidth() - 270, 120)

		# ????
		self.ViewDistance = ui.TextLine()
		self.ViewDistance.SetFontName(localeInfo.UI_DEF_FONT)
		self.ViewDistance.SetPosition(0, 0)
		
		##Ufuk Rina Saat
		#self.timeLine.SetWindowHorizontalAlignCenter()
		#self.timeLine.SetHorizontalAlignCenter()
		#self.timeLine.SetFeather()
		#self.timeLine.SetOutline()
		#self.timeLine.Show()		

	def __NotifyError(self, msg):
		chat.AppendChat(chat.CHAT_TYPE_INFO, msg)

	def ChangePKMode(self):

		if not app.IsPressed(app.DIK_LCONTROL):
			return

		if player.GetStatus(player.LEVEL)<constInfo.PVPMODE_PROTECTED_LEVEL:
			self.__NotifyError(localeInfo.OPTION_PVPMODE_PROTECT % (constInfo.PVPMODE_PROTECTED_LEVEL))
			return

		curTime = app.GetTime()
		if curTime - self.lastPKModeSendedTime < constInfo.PVPMODE_ACCELKEY_DELAY:
			return

		self.lastPKModeSendedTime = curTime

		curPKMode = player.GetPKMode()
		nextPKMode = curPKMode + 1
		if nextPKMode == player.PK_MODE_PROTECT:
			if 0 == player.GetGuildID():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.OPTION_PVPMODE_CANNOT_SET_GUILD_MODE)
				nextPKMode = 0
			else:
				nextPKMode = player.PK_MODE_GUILD

		elif nextPKMode == player.PK_MODE_MAX_NUM:
			nextPKMode = 0

		net.SendChatPacket("/PKMode " + str(nextPKMode))
		print "/PKMode " + str(nextPKMode)

	def OnChangePKMode(self):

		self.interface.OnChangePKMode()

		try:
			self.__NotifyError(localeInfo.OPTION_PVPMODE_MESSAGE_DICT[player.GetPKMode()])
		except KeyError:
			print "UNKNOWN PVPMode[%d]" % (player.GetPKMode())

		if constInfo.PVPMODE_TEST_ENABLE:
			curPKMode = player.GetPKMode()
			alignment, grade = chr.testGetPKData()
			self.pkModeNameDict = { 0 : "PEACE", 1 : "REVENGE", 2 : "FREE", 3 : "PROTECT", }
			self.testPKMode.SetText("Current PK Mode : " + self.pkModeNameDict.get(curPKMode, "UNKNOWN"))
			self.testAlignment.SetText("Current Alignment : " + str(alignment) + " (" + localeInfo.TITLE_NAME_LIST[grade] + ")")

	###############################################################################################
	###############################################################################################
	## Game Callback Functions

	# Start
	def StartGame(self):
		self.RefreshInventory()
		self.RefreshEquipment()
		self.RefreshCharacter()
		self.RefreshSkill()
		
		# MOVE_CHANNEL
		import serverInfo
		
		regionID = constInfo.REGION_ID
		serverID = constInfo.SERVER_ID
		channelID = constInfo.CHANNEL_ID

		net.SetServerInfo("'asd','aswd'")
		constInfo.RELOAD_SERVERINFO = True
		
		# END_OF_MOVE_CHANNEL
		
		if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
			systemSetting.SetNightModeOption(systemSetting.GetNightModeOption())
			systemSetting.SetSnowModeOption(systemSetting.GetSnowModeOption())
			systemSetting.SetSnowTextureModeOption(systemSetting.GetSnowTextureModeOption())

	if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
		def BINARY_Recv_Night_Mode(self, mode):
			self.__DayMode_Update(mode)
			
	# Refresh
	def CheckGameButton(self):
		if self.interface:
			self.interface.CheckGameButton()

	def RefreshAlignment(self):
		self.interface.RefreshAlignment()
		
	if app.WJ_SHOW_ALL_CHANNEL:
		def BINARY_OnChannelPacket(self, channel):
			import net
			dict = {'name' : '|cFFFFA500FORNAX'} # Replace with your server name.
			net.SetServerInfo((localeInfo.TEXT_CHANNEL % (dict['name'], channel)).strip())
			if self.interface:
				self.interface.wndMiniMap.serverInfo.SetText(net.GetServerInfo())		

	def RefreshStatus(self):
		self.CheckGameButton()

		if self.interface:
			self.interface.RefreshStatus()

		if self.playerGauge:
			self.playerGauge.RefreshGauge()

	def RefreshStamina(self):
		self.interface.RefreshStamina()

	def RefreshSkill(self):
		self.CheckGameButton()
		if self.interface:
			self.interface.RefreshSkill()

	def RefreshQuest(self):
		self.interface.RefreshQuest()

	def RefreshMessenger(self):
		self.interface.RefreshMessenger()

	def RefreshGuildInfoPage(self):
		self.interface.RefreshGuildInfoPage()

	def RefreshGuildBoardPage(self):
		self.interface.RefreshGuildBoardPage()

	def RefreshGuildMemberPage(self):
		self.interface.RefreshGuildMemberPage()

	def RefreshGuildMemberPageGradeComboBox(self):
		self.interface.RefreshGuildMemberPageGradeComboBox()

	def RefreshGuildSkillPage(self):
		self.interface.RefreshGuildSkillPage()

	def RefreshGuildGradePage(self):
		self.interface.RefreshGuildGradePage()

	if app.ENABLE_GUILDRENEWAL_SYSTEM:
		## guild_renewal
		def RefreshGuildBaseInfoPage(self):
			self.interface.RefreshGuildBaseInfoPage()

		## guild_renewal_war
		def RefreshGuildWarInfoPage(self):
			self.interface.RefreshGuildWarInfoPage()

	def RefreshMobile(self):
		if self.interface:
			self.interface.RefreshMobile()

	def OnMobileAuthority(self):
		self.interface.OnMobileAuthority()

	def OnBlockMode(self, mode):
		self.interface.OnBlockMode(mode)

	if app.ENABLE_HIDE_COSTUME_SYSTEM:
		def SetBodyCostumeHidden(self, hidden):
			constInfo.HIDDEN_BODY_COSTUME = int(hidden)
			self.interface.RefreshVisibleCostume()

		def SetHairCostumeHidden(self, hidden):
			constInfo.HIDDEN_HAIR_COSTUME = int(hidden)
			self.interface.RefreshVisibleCostume()

		def SetAcceCostumeHidden(self, hidden):
			if app.ENABLE_SASH_SYSTEM:
				constInfo.HIDDEN_ACCE_COSTUME = int(hidden)
				self.interface.RefreshVisibleCostume()
			else:
				pass

		def SetWeaponCostumeHidden(self, hidden):
			if app.ENABLE_COSTUME_WEAPON_SYSTEM:
				constInfo.HIDDEN_WEAPON_COSTUME = int(hidden)
				self.interface.RefreshVisibleCostume()
			else:
				pass

	#def OpenQuestWindow(self, skin, idx):
	#	if constInfo.INPUT_IGNORE == 1:
	#		return	
	#	self.interface.OpenQuestWindow(skin, idx)
		
	def HideAllQuestWindow(self):
		self.interface.HideAllQuestWindow()	

	def ConfirmPetName(self):
		guildName = self.guildNameBoard.GetText()
		if not guildName:
			return False

		if len(guildName) < 4 or len(guildName) > 13:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.INVALID_PET_NAME)
			return False

		net.RequestPetName(False, guildName)
		self.guildNameBoard.Close()
		self.guildNameBoard = None
		return True

	def AskGuildName(self):

		guildNameBoard = uiCommon.InputDialog()
		guildNameBoard.SetTitle(localeInfo.GUILD_NAME)
		guildNameBoard.SetAcceptEvent(ui.__mem_func__(self.ConfirmGuildName))
		guildNameBoard.SetCancelEvent(ui.__mem_func__(self.CancelGuildName))
		guildNameBoard.Open()

		self.guildNameBoard = guildNameBoard

	def ConfirmGuildName(self):
		guildName = self.guildNameBoard.GetText()
		if not guildName:
			return False

		if net.IsInsultIn(guildName):
			self.PopupMessage(localeInfo.GUILD_CREATE_ERROR_INSULT_NAME)
			return False

		net.SendAnswerMakeGuildPacket(guildName)
		self.guildNameBoard.Close()
		self.guildNameBoard = None
		return True

	def CancelGuildName(self):
		self.guildNameBoard.Close()
		self.guildNameBoard = None
		return True

	## Refine
	def PopupMessage(self, msg):
		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg, 0, localeInfo.UI_OK)

	def OpenRefineDialog(self, targetItemPos, nextGradeItemVnum, cost, prob, type=0):
		self.interface.OpenRefineDialog(targetItemPos, nextGradeItemVnum, cost, prob, type)

	def AppendMaterialToRefineDialog(self, vnum, count):
		self.interface.AppendMaterialToRefineDialog(vnum, count)

	def RunUseSkillEvent(self, slotIndex, coolTime):
		self.interface.OnUseSkill(slotIndex, coolTime)

	def ClearAffects(self):
		self.affectShower.ClearAffects()

	def SetAffect(self, affect):
		return
		self.affectShower.SetAffect(affect)

	def ResetAffect(self, affect):
		self.affectShower.ResetAffect(affect)

	# UNKNOWN_UPDATE
	def BINARY_NEW_AddAffect(self, type, pointIdx, value, duration, affType):
		self.affectShower.BINARY_NEW_AddAffect(type, pointIdx, value, duration, affType)
		if chr.NEW_AFFECT_DRAGON_SOUL_DECK1 == type or chr.NEW_AFFECT_DRAGON_SOUL_DECK2 == type:
			self.interface.DragonSoulActivate(type - chr.NEW_AFFECT_DRAGON_SOUL_DECK1)
			
		elif chr.NEW_AFFECT_DRAGON_SOUL_QUALIFIED == type:
			self.BINARY_DragonSoulGiveQuilification()
						
	def BINARY_NEW_RemoveAffect(self, type, pointIdx):
		self.affectShower.BINARY_NEW_RemoveAffect(type, pointIdx)
		if chr.NEW_AFFECT_DRAGON_SOUL_DECK1 == type or chr.NEW_AFFECT_DRAGON_SOUL_DECK2 == type:
			self.interface.DragonSoulDeactivate()
 
	# END_OF_UNKNOWN_UPDATE

	def ActivateSkillSlot(self, slotIndex):
		if self.interface:
			self.interface.OnActivateSkill(slotIndex)

	def DeactivateSkillSlot(self, slotIndex):
		if self.interface:
			self.interface.OnDeactivateSkill(slotIndex)

	def RefreshEquipment(self):
		if self.interface:
			self.interface.RefreshInventory()

	def RefreshInventory(self):
		if self.interface:
			self.interface.RefreshInventory()

	def RefreshCharacter(self):
		if self.interface:
			self.interface.RefreshCharacter()

	def OnGameOver(self):
		self.CloseTargetBoard()
		self.OpenRestartDialog()

	def OpenRestartDialog(self):
		self.interface.OpenRestartDialog()

	def ChangeCurrentSkill(self, skillSlotNumber):
		self.interface.OnChangeCurrentSkill(skillSlotNumber)

	## TargetBoard
	def SetPCTargetBoard(self, vid, name):
		self.targetBoard.Open(vid, name)
		
		if constInfo.GUILDSTORAGE["open"] == 1:
			return		
		
		if app.IsPressed(app.DIK_LCONTROL):
			
			if not player.IsSameEmpire(vid):
				return

			if player.IsMainCharacterIndex(vid):
				return		
			elif chr.INSTANCE_TYPE_BUILDING == chr.GetInstanceType(vid):
				return

			self.interface.OpenWhisperDialog(name)
			

	def RefreshTargetBoardByVID(self, vid):
		self.targetBoard.RefreshByVID(vid)

	def TargetBoardSetAffect(self, vid, affType, affDur):
		self.targetBoard.affectShower.TargetBoardSetAffect(vid, affType, affDur)

	def RefreshTargetBoardByName(self, name):
		self.targetBoard.RefreshByName(name)
		
	def __RefreshTargetBoard(self):
		self.targetBoard.Refresh()
		
	if app.ENABLE_VIEW_ELEMENT:
		def SetHPTargetBoard(self, vid, hpPercentage, bElement = -1):
			if vid != self.targetBoard.GetTargetVID():
				self.targetBoard.ResetTargetBoard()
				self.targetBoard.SetEnemyVID(vid)
			
			self.targetBoard.SetHP(hpPercentage)
			self.targetBoard.SetElementImage(bElement)
			self.targetBoard.Show()
	else:
		def SetHPTargetBoard(self, vid, hpPercentage):
			if vid != self.targetBoard.GetTargetVID():
				self.targetBoard.ResetTargetBoard()
				self.targetBoard.SetEnemyVID(vid)

			self.targetBoard.SetHP(hpPercentage)
			self.targetBoard.Show()
		
	#def SetHPTargetBoard(self, vid, hpPercentage):
	#	if vid != self.targetBoard.GetTargetVID():
	#		self.targetBoard.ResetTargetBoard()
	#		self.targetBoard.SetEnemyVID(vid)
   	#
	#	self.targetBoard.SetHP(hpPercentage)
	#	self.targetBoard.Show()

	def CloseTargetBoardIfDifferent(self, vid):
		if vid != self.targetBoard.GetTargetVID():
			self.targetBoard.Close()

	def CloseTargetBoard(self):
		self.targetBoard.Close()

	## View Equipment
	def OpenEquipmentDialog(self, vid):
		self.interface.OpenEquipmentDialog(vid)

	def SetEquipmentDialogItem(self, vid, slotIndex, vnum, count):
		self.interface.SetEquipmentDialogItem(vid, slotIndex, vnum, count)

	def SetEquipmentDialogSocket(self, vid, slotIndex, socketIndex, value):
		self.interface.SetEquipmentDialogSocket(vid, slotIndex, socketIndex, value)

	def SetEquipmentDialogAttr(self, vid, slotIndex, attrIndex, type, value):
		self.interface.SetEquipmentDialogAttr(vid, slotIndex, attrIndex, type, value)

	# SHOW_LOCAL_MAP_NAME
	def ShowMapName(self, mapName, x, y):

		if self.mapNameShower:
			self.mapNameShower.ShowMapName(mapName, x, y)

		if self.interface:
			self.interface.SetMapName(mapName)
	# END_OF_SHOW_LOCAL_MAP_NAME	

	def BINARY_OpenAtlasWindow(self):
		self.interface.BINARY_OpenAtlasWindow()

	## Chat
	def OnRecvWhisper(self, mode, name, line):
		if mode == chat.WHISPER_TYPE_GM:
			self.interface.RegisterGameMasterName(name)
		chat.AppendWhisper(mode, name, line)
		self.interface.RecvWhisper(name)

	def OnRecvWhisperSystemMessage(self, mode, name, line):
		chat.AppendWhisper(chat.WHISPER_TYPE_SYSTEM, name, line)
		self.interface.RecvWhisper(name)

	def OnRecvWhisperError(self, mode, name, line):
		if localeInfo.WHISPER_ERROR.has_key(mode):
			if app.OFFLINE_MESSAGE:
				chat.AppendWhisper(chat.WHISPER_TYPE_SYSTEM, name, name + localeInfo.OFFLINE_MESSAGE_WHISPER)
			else:
				chat.AppendWhisper(chat.WHISPER_TYPE_SYSTEM, name, localeInfo.WHISPER_ERROR[mode](name))
		else:
			chat.AppendWhisper(chat.WHISPER_TYPE_SYSTEM, name, "Whisper Unknown Error(mode=%d, name=%s)" % (mode, name))
		self.interface.RecvWhisper(name)

	def RecvWhisper(self, name):
		self.interface.RecvWhisper(name)

	#def OnPickMoney(self, money):
	#	self.interface.OnPickMoneyNew(money)
	#	if constInfo.Yang == 1:
	#		chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.GAME_PICK_MONEY % (money))
	#	if app.ENABLE_CHEQUE_SYSTEM:
	#		def OnPickCheque(self, cheque):
	#			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.CHEQUE_SYSTEM_PICK_WON % (cheque))			
	#	else:
	#		return
			
	def OnPickMoney(self, money):
		if constInfo.Yang == 1:
			self.interface.OnPickMoneyNew(money)
		if app.ENABLE_CHEQUE_SYSTEM:
			def OnPickCheque(self, cheque):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.CHEQUE_SYSTEM_PICK_WON % (cheque))			
		else:
			return

	def OnShopError(self, type):
		try:
			self.PopupMessage(localeInfo.SHOP_ERROR_DICT[type])
		except KeyError:
			self.PopupMessage(localeInfo.SHOP_ERROR_UNKNOWN % (type))

	def OnSafeBoxError(self):
		self.PopupMessage(localeInfo.SAFEBOX_ERROR)

	def OnFishingSuccess(self, isFish, fishName):
		chat.AppendChatWithDelay(chat.CHAT_TYPE_INFO, localeInfo.FISHING_SUCCESS(isFish, fishName), 2000)

	# ADD_FISHING_MESSAGE
	def OnFishingNotifyUnknown(self):
		chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.FISHING_UNKNOWN)

	def OnFishingWrongPlace(self):
		chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.FISHING_WRONG_PLACE)
	# END_OF_ADD_FISHING_MESSAGE

	def OnFishingNotify(self, isFish, fishName):
		chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.FISHING_NOTIFY(isFish, fishName))

	def OnFishingFailure(self):
		chat.AppendChatWithDelay(chat.CHAT_TYPE_INFO, localeInfo.FISHING_FAILURE, 2000)

	def OnCannotPickItem(self):
		chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.GAME_CANNOT_PICK_ITEM)

	# MINING
	def OnCannotMining(self):
		chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.GAME_CANNOT_MINING)
	# END_OF_MINING

	def OnCannotUseSkill(self, vid, type):
		if localeInfo.USE_SKILL_ERROR_TAIL_DICT.has_key(type):
			textTail.RegisterInfoTail(vid, localeInfo.USE_SKILL_ERROR_TAIL_DICT[type])

		if localeInfo.USE_SKILL_ERROR_CHAT_DICT.has_key(type):
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.USE_SKILL_ERROR_CHAT_DICT[type])

	def	OnCannotShotError(self, vid, type):
		textTail.RegisterInfoTail(vid, localeInfo.SHOT_ERROR_TAIL_DICT.get(type, localeInfo.SHOT_ERROR_UNKNOWN % (type)))

	## PointReset
	def StartPointReset(self):
		self.interface.OpenPointResetDialog()

	## Shop
	def StartShop(self, vid):
		self.interface.OpenShopDialog(vid)

	def EndShop(self):
		self.interface.CloseShopDialog()

	def RefreshShop(self):
		self.interface.RefreshShopDialog()

	def SetShopSellingPrice(self, Price):
		pass

	## Exchange
	def StartExchange(self):
		if constInfo.GUILDSTORAGE["open"] == 1:
			net.SendExchangeExitPacket()
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Nem kereskedhetsz ameddig a c? rakt? nyitva van.")
			return	
		self.interface.StartExchange()

	def EndExchange(self):
		self.interface.EndExchange()

	def RefreshExchange(self):
		self.interface.RefreshExchange()

	## Party
	def RecvPartyInviteQuestion(self, leaderVID, leaderName):
		partyInviteQuestionDialog = uiCommon.QuestionDialogWithTimeLimit()
		partyInviteQuestionDialog.SetText1(leaderName + localeInfo.PARTY_DO_YOU_JOIN)
		partyInviteQuestionDialog.SetTimeOverMsg(localeInfo.PARTY_ANSWER_TIMEOVER)
		partyInviteQuestionDialog.SetTimeOverEvent(self.AnswerPartyInvite, False)
		partyInviteQuestionDialog.SetAcceptEvent(lambda arg=True: self.AnswerPartyInvite(arg))
		partyInviteQuestionDialog.SetCancelEvent(lambda arg=False: self.AnswerPartyInvite(arg))
		partyInviteQuestionDialog.Open(10)
		partyInviteQuestionDialog.partyLeaderVID = leaderVID
		self.partyInviteQuestionDialog = partyInviteQuestionDialog

	def AnswerPartyInvite(self, answer):

		if not self.partyInviteQuestionDialog:
			return

		partyLeaderVID = self.partyInviteQuestionDialog.partyLeaderVID

		distance = player.GetCharacterDistance(partyLeaderVID)
		if distance < 0.0 or distance > 5000:
			answer = False

		net.SendPartyInviteAnswerPacket(partyLeaderVID, answer)

		self.partyInviteQuestionDialog.Close()
		self.partyInviteQuestionDialog = None

	def AddPartyMember(self, pid, name):
		self.interface.AddPartyMember(pid, name)

	def UpdatePartyMemberInfo(self, pid):
		self.interface.UpdatePartyMemberInfo(pid)

	def RemovePartyMember(self, pid):
		self.interface.RemovePartyMember(pid)
		self.__RefreshTargetBoard()

	def LinkPartyMember(self, pid, vid):
		self.interface.LinkPartyMember(pid, vid)

	def UnlinkPartyMember(self, pid):
		self.interface.UnlinkPartyMember(pid)

	def UnlinkAllPartyMember(self):
		self.interface.UnlinkAllPartyMember()

	def ExitParty(self):
		self.interface.ExitParty()
		self.RefreshTargetBoardByVID(self.targetBoard.GetTargetVID())

	def ChangePartyParameter(self, distributionMode):
		self.interface.ChangePartyParameter(distributionMode)

	## Messenger
	def OnMessengerAddFriendQuestion(self, name):
		messengerAddFriendQuestion = uiCommon.QuestionDialogWithTimeLimit()
		messengerAddFriendQuestion.SetText1(localeInfo.MESSENGER_DO_YOU_ACCEPT_ADD_FRIEND_1 % (name))
		messengerAddFriendQuestion.SetText2(localeInfo.MESSENGER_DO_YOU_ACCEPT_ADD_FRIEND_2)
		messengerAddFriendQuestion.SetTimeOverEvent(self.OnDenyAddFriend)
		messengerAddFriendQuestion.SetAcceptEvent(ui.__mem_func__(self.OnAcceptAddFriend))
		messengerAddFriendQuestion.SetCancelEvent(ui.__mem_func__(self.OnDenyAddFriend))
		messengerAddFriendQuestion.Open(10)
		messengerAddFriendQuestion.name = name
		self.messengerAddFriendQuestion = messengerAddFriendQuestion

	def OnAcceptAddFriend(self):
		name = self.messengerAddFriendQuestion.name
		net.SendChatPacket("/messenger_auth y " + name)
		self.OnCloseAddFriendQuestionDialog()
		return True

	def OnDenyAddFriend(self):
		name = self.messengerAddFriendQuestion.name
		net.SendChatPacket("/messenger_auth n " + name)
		self.OnCloseAddFriendQuestionDialog()
		return True

	def OnCloseAddFriendQuestionDialog(self):
		self.messengerAddFriendQuestion.Close()
		self.messengerAddFriendQuestion = None
		return True

	## SafeBox
	def OpenSafeboxWindow(self, size):
		self.interface.OpenSafeboxWindow(size)

	def RefreshSafebox(self):
		self.interface.RefreshSafebox()

	def RefreshSafeboxMoney(self):
		self.interface.RefreshSafeboxMoney()

	# ITEM_MALL
	def OpenMallWindow(self, size):
		self.interface.OpenMallWindow(size)

	def RefreshMall(self):
		self.interface.RefreshMall()
	# END_OF_ITEM_MALL

	## Guild
	def RecvGuildInviteQuestion(self, guildID, guildName):
		guildInviteQuestionDialog = uiCommon.QuestionDialog()
		guildInviteQuestionDialog.SetText(guildName + localeInfo.GUILD_DO_YOU_JOIN)
		guildInviteQuestionDialog.SetAcceptEvent(lambda arg=True: self.AnswerGuildInvite(arg))
		guildInviteQuestionDialog.SetCancelEvent(lambda arg=False: self.AnswerGuildInvite(arg))
		guildInviteQuestionDialog.Open()
		guildInviteQuestionDialog.guildID = guildID
		self.guildInviteQuestionDialog = guildInviteQuestionDialog

	def AnswerGuildInvite(self, answer):

		if not self.guildInviteQuestionDialog:
			return

		guildLeaderVID = self.guildInviteQuestionDialog.guildID
		net.SendGuildInviteAnswerPacket(guildLeaderVID, answer)

		self.guildInviteQuestionDialog.Close()
		self.guildInviteQuestionDialog = None

	
	def DeleteGuild(self):
		self.interface.DeleteGuild()

	## Clock
	def ShowClock(self, second):
		self.interface.ShowClock(second)

	def HideClock(self):
		self.interface.HideClock()

	## Emotion
	def BINARY_ActEmotion(self, emotionIndex):
		if self.interface.wndCharacter:
			self.interface.wndCharacter.ActEmotion(emotionIndex)

	###############################################################################################
	###############################################################################################
	## Keyboard Functions

	def CheckFocus(self):
		if False == self.IsFocus():
			if True == self.interface.IsOpenChat():
				self.interface.ToggleChat()

			self.SetFocus()

	def SaveScreen(self):
		chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.SAVE_SCREENSHOT_TEXT)
		print "save screen"

		# SCREENSHOT_CWDSAVE
		if SCREENSHOT_CWDSAVE:
			if not os.path.exists(os.getcwd()+os.sep+"Data/screenshot"):
				os.mkdir(os.getcwd()+os.sep+"Data/screenshot")

			(succeeded, name) = grp.SaveScreenShotToPath(os.getcwd()+os.sep+"Data/screenshot"+os.sep)
		elif SCREENSHOT_DIR:
			(succeeded, name) = grp.SaveScreenShot(SCREENSHOT_DIR)
		else:
			(succeeded, name) = grp.SaveScreenShot()
		# END_OF_SCREENSHOT_CWDSAVE

		if succeeded:
			pass
			"""
			chat.AppendChat(chat.CHAT_TYPE_INFO, name + localeInfo.SCREENSHOT_SAVE1)
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.SCREENSHOT_SAVE2)
			"""
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.SCREENSHOT_SAVE_FAILURE)

	def ShowConsole(self):
		if __DEBUG__ or self.consoleEnable:
			player.EndKeyWalkingImmediately()
			self.console.OpenWindow()

	def ShowName(self):
		self.ShowNameFlag = True
		self.playerGauge.EnableShowAlways()
		player.SetQuickPage(self.quickSlotPageIndex+1)

	# ADD_ALWAYS_SHOW_NAME
	def __IsShowName(self):

		if systemSetting.IsAlwaysShowName():
			return True

		if self.ShowNameFlag:
			return True

		return False
	# END_OF_ADD_ALWAYS_SHOW_NAME
	
	def HideName(self):
		self.ShowNameFlag = False
		self.playerGauge.DisableShowAlways()
		player.SetQuickPage(self.quickSlotPageIndex)

	def ShowMouseImage(self):
		pass
		#self.interface.ShowMouseImage()

	def HideMouseImage(self):
		pass
		#self.interface.HideMouseImage()

	def StartAttack(self):
		player.SetAttackKeyState(True)

	def EndAttack(self):
		player.SetAttackKeyState(False)


	def MoveUp(self):
		player.SetSingleDIKKeyState(app.DIK_UP, True)

	def MoveDown(self):
		player.SetSingleDIKKeyState(app.DIK_DOWN, True)

	def MoveLeft(self):
		player.SetSingleDIKKeyState(app.DIK_LEFT, True)

	def MoveRight(self):
		player.SetSingleDIKKeyState(app.DIK_RIGHT, True)

	def StopUp(self):
		player.SetSingleDIKKeyState(app.DIK_UP, False)

	def StopDown(self):
		player.SetSingleDIKKeyState(app.DIK_DOWN, False)

	def StopLeft(self):
		player.SetSingleDIKKeyState(app.DIK_LEFT, False)

	def StopRight(self):
		player.SetSingleDIKKeyState(app.DIK_RIGHT, False)

	def PickUpItem(self):
		player.PickCloseItem()

	###############################################################################################
	###############################################################################################
	## Event Handler

	def OnKeyDown(self, key):
		if self.interface.wndWeb and self.interface.wndWeb.IsShow():
			return

		if key == app.DIK_ESC:
			self.RequestDropItem(False)
			constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

		try:
			self.onPressKeyDict[key]()
		except KeyError:
			pass
		except:
			raise

		return True

	def OnKeyUp(self, key):
		try:
			self.onClickKeyDict[key]()
		except KeyError:
			pass
		except:
			raise

		return True

	def OnMouseLeftButtonDown(self):
		if self.interface.BUILD_OnMouseLeftButtonDown():
			return

		if mouseModule.mouseController.isAttached():
			self.CheckFocus()
		else:
			hyperlink = ui.GetHyperlink()
			if hyperlink:
				return
			else:
				self.CheckFocus()
				player.SetMouseState(player.MBT_LEFT, player.MBS_PRESS);

		return True

	def OnMouseLeftButtonUp(self):

		if self.interface.BUILD_OnMouseLeftButtonUp():
			return

		if mouseModule.mouseController.isAttached():

			attachedType = mouseModule.mouseController.GetAttachedType()
			attachedItemIndex = mouseModule.mouseController.GetAttachedItemIndex()
			attachedItemSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()
			attachedItemCount = mouseModule.mouseController.GetAttachedItemCount()

			## QuickSlot
			if player.SLOT_TYPE_QUICK_SLOT == attachedType:
				player.RequestDeleteGlobalQuickSlot(attachedItemSlotPos)

			## Inventory
			elif player.SLOT_TYPE_INVENTORY == attachedType:

				if player.ITEM_MONEY == attachedItemIndex:
					self.__PutMoney(attachedType, attachedItemCount, self.PickingCharacterIndex)
				else:
					self.__PutItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount, self.PickingCharacterIndex)

			## DragonSoul
			elif player.SLOT_TYPE_DRAGON_SOUL_INVENTORY == attachedType:
				self.__PutItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount, self.PickingCharacterIndex)

			elif app.ENABLE_SPECIAL_STORAGE and attachedType in (player.SLOT_TYPE_UPGRADE_INVENTORY, player.SLOT_TYPE_BOOK_INVENTORY, player.SLOT_TYPE_STONE_INVENTORY, player.SLOT_TYPE_CHESTS_INVENTORY):
				self.__PutItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount, self.PickingCharacterIndex)

			mouseModule.mouseController.DeattachObject()

		else:
			hyperlink = ui.GetHyperlink()
			if hyperlink:
				if app.IsPressed(app.DIK_LALT):
					link = chat.GetLinkFromHyperlink(hyperlink)
					ime.PasteString(link)
				else:
					self.interface.MakeHyperlinkTooltip(hyperlink)
				return
			else:
				player.SetMouseState(player.MBT_LEFT, player.MBS_CLICK)

		#player.EndMouseWalking()
		return True

#	def __PutItem(self, attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount, dstChrID):
#		if player.SLOT_TYPE_INVENTORY == attachedType or player.SLOT_TYPE_DRAGON_SOUL_INVENTORY == attachedType:
#			attachedInvenType = player.SlotTypeToInvenType(attachedType)
#			if True == chr.HasInstance(self.PickingCharacterIndex) and player.GetMainCharacterIndex() != dstChrID:
#				if player.IsEquipmentSlot(attachedItemSlotPos) and player.SLOT_TYPE_DRAGON_SOUL_INVENTORY != attachedType:
#					self.stream.popupWindow.Close()
#					self.stream.popupWindow.Open(localeInfo.EXCHANGE_FAILURE_EQUIP_ITEM, 0, localeInfo.UI_OK)
#				else:
#					if chr.IsNPC(dstChrID):
#						net.SendGiveItemPacket(dstChrID, attachedInvenType, attachedItemSlotPos, attachedItemCount)
#					else:
#						net.SendExchangeStartPacket(dstChrID)
#						net.SendExchangeItemAddPacket(attachedInvenType, attachedItemSlotPos, 0)
#			else:
#				self.__DropItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount)

	def __PutItem(self, attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount, dstChrID):
		if player.SLOT_TYPE_INVENTORY == attachedType or player.SLOT_TYPE_DRAGON_SOUL_INVENTORY == attachedType or\
			app.ENABLE_SPECIAL_STORAGE and attachedType in (player.SLOT_TYPE_UPGRADE_INVENTORY, player.SLOT_TYPE_BOOK_INVENTORY, player.SLOT_TYPE_STONE_INVENTORY, player.SLOT_TYPE_CHESTS_INVENTORY):
			attachedInvenType = player.SlotTypeToInvenType(attachedType)
			if True == chr.HasInstance(self.PickingCharacterIndex) and player.GetMainCharacterIndex() != dstChrID:
				if player.IsEquipmentSlot(attachedItemSlotPos) and player.SLOT_TYPE_DRAGON_SOUL_INVENTORY != attachedType:
					self.stream.popupWindow.Close()
					self.stream.popupWindow.Open(localeInfo.EXCHANGE_FAILURE_EQUIP_ITEM, 0, localeInfo.UI_OK)
				else:
					if chr.IsNPC(dstChrID):
						net.SendGiveItemPacket(dstChrID, attachedInvenType, attachedItemSlotPos, attachedItemCount)
						
						if app.ENABLE_REFINE_RENEWAL:
							constInfo.AUTO_REFINE_TYPE = 2
							constInfo.AUTO_REFINE_DATA["NPC"][0] = dstChrID
							constInfo.AUTO_REFINE_DATA["NPC"][1] = attachedInvenType
							constInfo.AUTO_REFINE_DATA["NPC"][2] = attachedItemSlotPos
							constInfo.AUTO_REFINE_DATA["NPC"][3] = attachedItemCount
						
					else:
						net.SendExchangeStartPacket(dstChrID)
						net.SendExchangeItemAddPacket(attachedInvenType, attachedItemSlotPos, 0)
			else:
				self.__DropItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount)


	def __PutMoney(self, attachedType, attachedMoney, dstChrID, attachedCheque = None):
		if True == chr.HasInstance(dstChrID) and player.GetMainCharacterIndex() != dstChrID:
			net.SendExchangeStartPacket(dstChrID)
			net.SendExchangeElkAddPacket(attachedMoney)
			net.SendExchangeElkAddPacket(attachedCheque)
		else:
			self.__DropMoney(attachedType, attachedMoney, attachedCheque)

	def __DropMoney(self, attachedType, attachedMoney, attachedCheque):
		# PRIVATESHOP_DISABLE_ITEM_DROP - ???? ?? ?? ?? ??? ?? ??
		if uiPrivateShopBuilder.IsBuildingPrivateShop():			
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.DROP_ITEM_FAILURE_PRIVATE_SHOP)
			return
		# END_OF_PRIVATESHOP_DISABLE_ITEM_DROP
		
		if attachedMoney>=1000:
			self.stream.popupWindow.Close()
			self.stream.popupWindow.Open(localeInfo.CHEQUE_SYSTEM_DO_NOT_DROP_MONEY, 0, localeInfo.UI_OK)
			return
			
		if attachedCheque<=0:
			self.stream.popupWindow.Close()
			self.stream.popupWindow.Open(localeInfo.CHEQUE_SYSTEM_DO_NOT_DROP_MONEY, 0, localeInfo.UI_OK)
			return	

		itemDropQuestionDialog = uiCommon.QuestionDialog()
		itemDropQuestionDialog.SetText(localeInfo.DO_YOU_DROP_MONEY % (attachedMoney))
		itemDropQuestionDialog.SetText(localeInfo.DO_YOU_DROP_MONEY % (attachedCheque))
		itemDropQuestionDialog.SetAcceptEvent(lambda arg=True: self.RequestDropItem(arg))
		itemDropQuestionDialog.SetCancelEvent(lambda arg=False: self.RequestDropItem(arg))
		itemDropQuestionDialog.Open()
		itemDropQuestionDialog.dropType = attachedType
		itemDropQuestionDialog.dropCount = attachedCheque
		itemDropQuestionDialog.dropNumber = player.ITEM_CHEQUE
		self.itemDropQuestionDialog = itemDropQuestionDialog

	def __DropItem(self, attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount):
		# PRIVATESHOP_DISABLE_ITEM_DROP - ???? ?? ?? ?? ??? ?? ??
		if uiPrivateShopBuilder.IsBuildingPrivateShop():			
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.DROP_ITEM_FAILURE_PRIVATE_SHOP)
			return
		# END_OF_PRIVATESHOP_DISABLE_ITEM_DROP
		
		if player.SLOT_TYPE_INVENTORY == attachedType and player.IsEquipmentSlot(attachedItemSlotPos):
			self.stream.popupWindow.Close()
			self.stream.popupWindow.Open(localeInfo.DROP_ITEM_FAILURE_EQUIP_ITEM, 0, localeInfo.UI_OK)

		else:
			if attachedType in (player.SLOT_TYPE_SAFEBOX, player.SLOT_TYPE_PRIVATE_SHOP, player.SLOT_TYPE_MALL, player.SLOT_TYPE_EXCHANGE_OWNER, player.SLOT_TYPE_EXCHANGE_TARGET, player.SLOT_TYPE_QUICK_SLOT, player.SLOT_TYPE_EMOTION):
				return False
			
			window = player.SlotTypeToInvenType(attachedType)

			item.SelectItem(attachedItemIndex)
			dropItemName = item.GetItemName()

			## Question Text
			questionText = localeInfo.HOW_MANY_ITEM_DO_YOU_DROP(dropItemName, attachedItemCount)

			## Dialog
			itemDropQuestionDialog = uiCommon.QuestionDialog()
			itemDropQuestionDialog.SetText(questionText)
			itemDropQuestionDialog.SetAcceptEvent(lambda arg=TRUE: self.RequestDropItem(arg))
			itemDropQuestionDialog.SetCancelEvent(lambda arg=FALSE: self.RequestDropItem(arg))
			itemDropQuestionDialog.Open()
			itemDropQuestionDialog.dropType = attachedType
			itemDropQuestionDialog.dropNumber = attachedItemSlotPos
			itemDropQuestionDialog.dropCount = attachedItemCount
			self.itemDropQuestionDialog = itemDropQuestionDialog

			constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)
	
	def RequestDropItem(self, answer):
		if not self.itemDropQuestionDialog:
			return

		if answer:
			dropType = self.itemDropQuestionDialog.dropType
			dropCount = self.itemDropQuestionDialog.dropCount
			dropNumber = self.itemDropQuestionDialog.dropNumber
			window = player.SlotTypeToInvenType(dropType)

			if dropNumber == player.ITEM_MONEY:
				net.SendGoldDropPacketNew(dropCount)
				snd.PlaySound("sound/ui/money.wav")
			else:
				self.__SendDropItemPacket(dropNumber, dropCount, window)
	
		self.itemDropQuestionDialog.Close()
		self.itemDropQuestionDialog = None

		constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)	

	# PRIVATESHOP_DISABLE_ITEM_DROP
	def __SendDropItemPacket(self, itemVNum, itemCount, itemInvenType = player.INVENTORY):
		if uiPrivateShopBuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.DROP_ITEM_FAILURE_PRIVATE_SHOP)
			return

		net.SendItemDropPacketNew(itemInvenType, itemVNum, itemCount)
	# END_OF_PRIVATESHOP_DISABLE_ITEM_DROP

	def __SendSellItemPacket(self, itemVNum, itemInvenTyoe = player.INVENTORY):
		if uiPrivateShopBuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.DROP_ITEM_FAILURE_PRIVATE_SHOP)
			return
		if app.WJ_OFFLINESHOP_SYSTEM:
			if (uiOfflineShopBuilder.IsBuildingOfflineShop()):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.DROP_ITEM_FAILURE_OFFLINE_SHOP)
				return

			if (uiOfflineShop.IsEditingOfflineShop()):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.DROP_ITEM_FAILURE_OFFLINE_SHOP)
				return
		net.SendChatPacket("/itemsat %d" % (int(itemVNum)))

	def OnMouseRightButtonDown(self):

		self.CheckFocus()

		if True == mouseModule.mouseController.isAttached():
			mouseModule.mouseController.DeattachObject()

		else:
			player.SetMouseState(player.MBT_RIGHT, player.MBS_PRESS)

		return True

	def OnMouseRightButtonUp(self):
		if True == mouseModule.mouseController.isAttached():
			return True

		player.SetMouseState(player.MBT_RIGHT, player.MBS_CLICK)
		return True

	def OnMouseMiddleButtonDown(self):
		player.SetMouseMiddleButtonState(player.MBS_PRESS)

	def OnMouseMiddleButtonUp(self):
		player.SetMouseMiddleButtonState(player.MBS_CLICK)

	def OnUpdate(self):	
		app.UpdateGame()
		
		#localtime = localtime = time.strftime("%Y.%m.%d | %H:%M:%S")
		#self.timeLine.SetText(localtime)
		#self.timeLine.Show()
		
		if self.mapNameShower.IsShow():
			self.mapNameShower.Update()

		if self.isShowDebugInfo:
			self.UpdateDebugInfo()

		if self.enableXMasBoom:
			self.__XMasBoom_Update()

		self.interface.BUILD_OnUpdate()
		
		#htime = int(time.strftime("%H"))
		#if htime - makeitrain > 0 or htime - makeitrain < 0:
			#self.__MakeRain()  
			
		#if app.IsPressed(app.DIK_P) and app.IsPressed(app.DIK_LSHIFT):
		#	if self.GiftBox.IsShow():
		#		self.GiftBox.Hide()
		#	else:
		#		self.GiftBox.Show()			
		
		
	def UpdateDebugInfo(self):
		#
		# ??? ?? ? FPS ??
		(x, y, z) = player.GetMainCharacterPosition()
		nUpdateTime = app.GetUpdateTime()
		nUpdateFPS = app.GetUpdateFPS()
		nRenderFPS = app.GetRenderFPS()
		nFaceCount = app.GetFaceCount()
		fFaceSpeed = app.GetFaceSpeed()
		nST=background.GetRenderShadowTime()
		(fAveRT, nCurRT) =  app.GetRenderTime()
		(iNum, fFogStart, fFogEnd, fFarCilp) = background.GetDistanceSetInfo()
		(iPatch, iSplat, fSplatRatio, sTextureNum) = background.GetRenderedSplatNum()
		if iPatch == 0:
			iPatch = 1

		#(dwRenderedThing, dwRenderedCRC) = background.GZusbpvHuVMB4evxLT2rnTcU2efvbutLMA()

		self.PrintCoord.SetText("Coordinate: %.2f %.2f %.2f ATM: %d" % (x, y, z, app.GetAvailableTextureMemory()/(1024*1024)))
		xMouse, yMouse = wndMgr.GetMousePosition()
		self.PrintMousePos.SetText("MousePosition: %d %d" % (xMouse, yMouse))			

		self.FrameRate.SetText("UFPS: %3d UT: %3d FS %.2f" % (nUpdateFPS, nUpdateTime, fFaceSpeed))

		fAveRT = 2.0
		if fAveRT>1.0:
			self.Pitch.SetText("RFPS: %3d RT:%.2f(%3d) FC: %d(%.2f) " % (nRenderFPS, fAveRT, nCurRT, nFaceCount, nFaceCount/fAveRT))

		self.Splat.SetText("PATCH: %d SPLAT: %d BAD(%.2f)" % (iPatch, iSplat, fSplatRatio))
		#self.Pitch.SetText("Pitch: %.2f" % (app.GetCameraPitch())
		#self.TextureNum.SetText("TN : %s" % (sTextureNum))
		#self.ObjectNum.SetText("GTI : %d, CRC : %d" % (dwRenderedThing, dwRenderedCRC))
		self.ViewDistance.SetText("Num : %d, FS : %f, FE : %f, FC : %f" % (iNum, fFogStart, fFogEnd, fFarCilp))

	def OnRender(self):
		app.RenderGame()
		
		if self.console.Console.collision:
			background.RenderCollision()
			chr.RenderCollision()

		(x, y) = app.GetCursorPosition()

		########################
		# Picking
		########################
		textTail.UpdateAllTextTail()

		if True == wndMgr.IsPickedWindow(self.hWnd):

			self.PickingCharacterIndex = chr.Pick()

			if -1 != self.PickingCharacterIndex:
				textTail.ShowCharacterTextTail(self.PickingCharacterIndex)
			if 0 != self.targetBoard.GetTargetVID():
				textTail.ShowCharacterTextTail(self.targetBoard.GetTargetVID())

			# ADD_ALWAYS_SHOW_NAME
			if not self.__IsShowName():
				self.PickingItemIndex = item.Pick()
				if -1 != self.PickingItemIndex:
					textTail.ShowItemTextTail(self.PickingItemIndex)
			# END_OF_ADD_ALWAYS_SHOW_NAME
			
		## Show all name in the range
		
		# ADD_ALWAYS_SHOW_NAME
		if self.__IsShowName():
			textTail.ShowAllTextTail()
			self.PickingItemIndex = textTail.Pick(x, y)
		# END_OF_ADD_ALWAYS_SHOW_NAME

		if app.ENABLE_GRAPHIC_ON_OFF:
			if systemSetting.IsShowSalesText():
				uiPrivateShopBuilder.UpdateADBoard()
				# if app.WJ_OFFLINESHOP_SYSTEM:
					# uiOfflineShopBuilder.UpdateADBoard()

		textTail.UpdateShowingTextTail()
		textTail.ArrangeTextTail()
		if -1 != self.PickingItemIndex:
			textTail.SelectItemName(self.PickingItemIndex)

		grp.PopState()
		grp.SetInterfaceRenderState()

		textTail.Render()
		textTail.HideAllTextTail()

	def OnPressEscapeKey(self):
		if app.TARGET == app.GetCursor():
			app.SetCursor(app.NORMAL)
			
		elif True == mouseModule.mouseController.isAttached():
			mouseModule.mouseController.DeattachObject()

		else:
			self.interface.OpenSystemDialog()

		return True

	def OnIMEReturn(self):
		if app.IsPressed(app.DIK_LSHIFT):
			self.interface.OpenWhisperDialogWithoutTarget()
		else:
			self.interface.ToggleChat()
		return True

	def OnPressExitKey(self):
		self.interface.ToggleSystemDialog()
		return True

	## BINARY CALLBACK
	######################################################################################
	
	# EXCHANGE
	if app.WJ_ENABLE_TRADABLE_ICON:
		def BINARY_AddItemToExchange(self, inven_type, inven_pos, display_pos):
			if inven_type == player.INVENTORY:
				self.interface.CantTradableItemExchange(display_pos, inven_pos)
	# END_OF_EXCHANGE	
	
	# WEDDING
	def BINARY_LoverInfo(self, name, lovePoint):
		if self.interface.wndMessenger:
			self.interface.wndMessenger.OnAddLover(name, lovePoint)
		if self.affectShower:
			self.affectShower.SetLoverInfo(name, lovePoint)

	def BINARY_UpdateLovePoint(self, lovePoint):
		if self.interface.wndMessenger:
			self.interface.wndMessenger.OnUpdateLovePoint(lovePoint)
		if self.affectShower:
			self.affectShower.OnUpdateLovePoint(lovePoint)
	# END_OF_WEDDING
	
	if app.ENABLE_SEND_TARGET_INFO:
		def CMD_RecvTargetMonsterRespawnInfo(self, raceNum, respawnTime):
			raceNum = int(raceNum)
			if not raceNum in constInfo.MONSTER_INFO_DATA:
				constInfo.MONSTER_INFO_DATA.update({raceNum : {}})
				constInfo.MONSTER_INFO_DATA[raceNum].update({"items" : []})
				constInfo.MONSTER_INFO_DATA[raceNum].update({"respawn" : 0})
				
			constInfo.MONSTER_INFO_DATA[raceNum]["respawn"] = int(respawnTime)
			self.BINARY_RefreshTargetMonsterDropInfo(0)
			
		def BINARY_AddTargetMonsterDropInfo(self, raceNum, itemVnum, itemCount):
			if not raceNum in constInfo.MONSTER_INFO_DATA:
				constInfo.MONSTER_INFO_DATA.update({raceNum : {}})
				constInfo.MONSTER_INFO_DATA[raceNum].update({"items" : []})
				constInfo.MONSTER_INFO_DATA[raceNum].update({"respawn" : 0})
			curList = constInfo.MONSTER_INFO_DATA[raceNum]["items"]

			isUpgradeable = False
			isMetin = False
			item.SelectItem(itemVnum)
			if item.GetItemType() == item.ITEM_TYPE_WEAPON or item.GetItemType() == item.ITEM_TYPE_ARMOR:
				isUpgradeable = True
			elif item.GetItemType() == item.ITEM_TYPE_METIN:
				isMetin = True

			for curItem in curList:
				if isUpgradeable:
					if curItem.has_key("vnum_list") and curItem["vnum_list"][0] / 10 * 10 == itemVnum / 10 * 10:
						if not (itemVnum in curItem["vnum_list"]):
							curItem["vnum_list"].append(itemVnum)
						return
				elif isMetin:
					if curItem.has_key("vnum_list"):
						baseVnum = curItem["vnum_list"][0]
					if curItem.has_key("vnum_list") and (baseVnum - baseVnum%1000) == (itemVnum - itemVnum%1000):
						if not (itemVnum in curItem["vnum_list"]):
							curItem["vnum_list"].append(itemVnum)
						return
				else:
					if curItem.has_key("vnum") and curItem["vnum"] == itemVnum and curItem["count"] == itemCount:
						return

			if isUpgradeable or isMetin:
				curList.append({"vnum_list":[itemVnum], "count":itemCount})
			else:
				curList.append({"vnum":itemVnum, "count":itemCount})

		def BINARY_RefreshTargetMonsterDropInfo(self, raceNum):
			self.targetBoard.RefreshMonsterInfoBoard()	
	
	# QUEST_CONFIRM
	def BINARY_OnQuestConfirm(self, msg, timeout, pid):
		confirmDialog = uiCommon.QuestionDialogWithTimeLimit()
		confirmDialog.SetText1(msg)
		confirmDialog.Open(timeout)
		confirmDialog.SetAcceptEvent(lambda answer=True, pid=pid: net.SendQuestConfirmPacket(answer, pid) or self.confirmDialog.Hide())
		confirmDialog.SetCancelEvent(lambda answer=False, pid=pid: net.SendQuestConfirmPacket(answer, pid) or self.confirmDialog.Hide())
		self.confirmDialog = confirmDialog
    # END_OF_QUEST_CONFIRM

    # GIFT command
	#def Gift_Show(self):
	#	self.interface.ShowGift()

	# CUBE
	def BINARY_Cube_Open(self, npcVNUM):
		self.currentCubeNPC = npcVNUM
		
		self.interface.OpenCubeWindow()

		
		if npcVNUM not in self.cubeInformation:
			net.SendChatPacket("/cube r_info")
		else:
			cubeInfoList = self.cubeInformation[npcVNUM]
			
			i = 0
			for cubeInfo in cubeInfoList:								
				self.interface.wndCube.AddCubeResultItem(cubeInfo["vnum"], cubeInfo["count"])
				
				j = 0				
				for materialList in cubeInfo["materialList"]:
					for materialInfo in materialList:
						itemVnum, itemCount = materialInfo
						self.interface.wndCube.AddMaterialInfo(i, j, itemVnum, itemCount)
					j = j + 1						
						
				i = i + 1
				
			self.interface.wndCube.Refresh()

	def BINARY_Cube_Close(self):
		self.interface.CloseCubeWindow()

	# ??? ??? ??, ???? ???? VNUM? ?? ?? update
	def BINARY_Cube_UpdateInfo(self, gold, itemVnum, count):
		self.interface.UpdateCubeInfo(gold, itemVnum, count)

	#def oyuncu_black(self, black, sari, kirmizi, mavi):
	#	if self.interface:
	#		self.interface.wndMiniMap.online_cok_hojdir_ama_benane(black, sari, kirmizi, mavi)
		
	def BINARY_Cube_Succeed(self, itemVnum, count):
		print "?? ?? ??"
		self.interface.SucceedCubeWork(itemVnum, count)
		pass

	def BINARY_Cube_Failed(self):
		print "?? ?? ??"
		self.interface.FailedCubeWork()
		pass

	def BINARY_Cube_ResultList(self, npcVNUM, listText):
		# ResultList Text Format : 72723,1/72725,1/72730.1/50001,5  ????? "/" ??? ??? ???? ?
		#print listText
		
		if npcVNUM == 0:
			npcVNUM = self.currentCubeNPC
		
		self.cubeInformation[npcVNUM] = []
		
		try:
			for eachInfoText in listText.split("/"):
				eachInfo = eachInfoText.split(",")
				itemVnum	= int(eachInfo[0])
				itemCount	= int(eachInfo[1])

				self.cubeInformation[npcVNUM].append({"vnum": itemVnum, "count": itemCount})
				self.interface.wndCube.AddCubeResultItem(itemVnum, itemCount)
			
			resultCount = len(self.cubeInformation[npcVNUM])
			requestCount = 7
			modCount = resultCount % requestCount
			splitCount = resultCount / requestCount
			for i in xrange(splitCount):
				#print("/cube r_info %d %d" % (i * requestCount, requestCount))
				net.SendChatPacket("/cube r_info %d %d" % (i * requestCount, requestCount))
				
			if 0 < modCount:
				#print("/cube r_info %d %d" % (splitCount * requestCount, modCount))				
				net.SendChatPacket("/cube r_info %d %d" % (splitCount * requestCount, modCount))

		except RuntimeError, msg:
			dbg.TraceError(msg)
			return 0
			
		pass
		
	def BINARY_Cube_MaterialInfo(self, startIndex, listCount, listText):
		# Material Text Format : 125,1|126,2|127,2|123,5&555,5&555,4/120000
		try:
			#print listText
			
			if 3 > len(listText):
				dbg.TraceError("Wrong Cube Material Infomation")
				return 0

			
			
			eachResultList = listText.split("@")

			cubeInfo = self.cubeInformation[self.currentCubeNPC]			
			
			itemIndex = 0
			for eachResultText in eachResultList:
				cubeInfo[startIndex + itemIndex]["materialList"] = [[], [], [], [], []]
				materialList = cubeInfo[startIndex + itemIndex]["materialList"]
				
				gold = 0
				splitResult = eachResultText.split("/")
				if 1 < len(splitResult):
					gold = int(splitResult[1])
					
				#print "splitResult : ", splitResult
				eachMaterialList = splitResult[0].split("&")
				
				i = 0
				for eachMaterialText in eachMaterialList:
					complicatedList = eachMaterialText.split("|")
					
					if 0 < len(complicatedList):
						for complicatedText in complicatedList:
							(itemVnum, itemCount) = complicatedText.split(",")
							itemVnum = int(itemVnum)
							itemCount = int(itemCount)
							self.interface.wndCube.AddMaterialInfo(itemIndex + startIndex, i, itemVnum, itemCount)
							
							materialList[i].append((itemVnum, itemCount))
							
					else:
						itemVnum, itemCount = eachMaterialText.split(",")
						itemVnum = int(itemVnum)
						itemCount = int(itemCount)
						self.interface.wndCube.AddMaterialInfo(itemIndex + startIndex, i, itemVnum, itemCount)
						
						materialList[i].append((itemVnum, itemCount))
						
					i = i + 1
					
					
					
				itemIndex = itemIndex + 1
				
			self.interface.wndCube.Refresh()
			
				
		except RuntimeError, msg:
			dbg.TraceError(msg)
			return 0
			
		pass
	
	# END_OF_CUBE
	
	# ???		
	def BINARY_Highlight_Item(self, inven_type, inven_pos):
		if self.interface:
			self.interface.Highligt_Item(inven_type, inven_pos)	
		
	def BINARY_Cards_UpdateInfo(self, hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, hand_4, hand_4_v, hand_5, hand_5_v, cards_left, points):
		self.interface.UpdateCardsInfo(hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, hand_4, hand_4_v, hand_5, hand_5_v, cards_left, points)
	
	def BINARY_Cards_FieldUpdateInfo(self, hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points):
		self.interface.UpdateCardsFieldInfo(hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points)
	
	def BINARY_Cards_PutReward(self, hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points):
		self.interface.CardsPutReward(hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points)
	
	def BINARY_Cards_Open(self, safemode):
		self.interface.OpenCardsWindow(safemode)		
	
	def BINARY_DragonSoulGiveQuilification(self):
		self.interface.DragonSoulGiveQuilification()
		
	def BINARY_DragonSoulRefineWindow_Open(self):
		self.interface.OpenDragonSoulRefineWindow()

	def BINARY_DragonSoulRefineWindow_RefineFail(self, reason, inven_type, inven_pos):
		self.interface.FailDragonSoulRefine(reason, inven_type, inven_pos)

	def BINARY_DragonSoulRefineWindow_RefineSucceed(self, inven_type, inven_pos):
		self.interface.SucceedDragonSoulRefine(inven_type, inven_pos)
	
	# END of DRAGON SOUL REFINE WINDOW
	
	def BINARY_SetBigMessage(self, message):
		self.interface.bigBoard.SetTip(message)

	def BINARY_SetTipMessage(self, message):
		self.interface.tipBoard.SetTip(message)		

	def BINARY_AppendNotifyMessage(self, type):
		if not type in localeInfo.NOTIFY_MESSAGE:
			return
		chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.NOTIFY_MESSAGE[type])

	def BINARY_Guild_EnterGuildArea(self, areaID):
		self.interface.BULID_EnterGuildArea(areaID)

	def BINARY_Guild_ExitGuildArea(self, areaID):
		self.interface.BULID_ExitGuildArea(areaID)

	def BINARY_GuildWar_OnSendDeclare(self, guildID):
		pass

	if app.ENABLE_GUILDRENEWAL_SYSTEM and app.ENABLE_NEW_WAR_OPTIONS:
		def BINARY_GuildWar_OnRecvDeclare(self, guildID, warType, winType, ScoreType, TimeType):
			mainCharacterName = player.GetMainCharacterName()
			masterName = guild.GetGuildMasterName()
			if mainCharacterName == masterName:
				self.__GuildWar_OpenAskDialog(guildID, warType, winType, ScoreType, TimeType)
	else:
		def BINARY_GuildWar_OnRecvDeclare(self, guildID, warType):
			mainCharacterName = player.GetMainCharacterName()
			masterName = guild.GetGuildMasterName()
			if mainCharacterName == masterName:
				self.__GuildWar_OpenAskDialog(guildID, warType)

	def BINARY_GuildWar_OnRecvPoint(self, gainGuildID, opponentGuildID, point):
		self.interface.OnRecvGuildWarPoint(gainGuildID, opponentGuildID, point)	

	def BINARY_GuildWar_OnStart(self, guildSelf, guildOpp):
		self.interface.OnStartGuildWar(guildSelf, guildOpp)

	def BINARY_GuildWar_OnEnd(self, guildSelf, guildOpp):
		self.interface.OnEndGuildWar(guildSelf, guildOpp)

	def BINARY_BettingGuildWar_SetObserverMode(self, isEnable):
		self.interface.BINARY_SetObserverMode(isEnable)

	def BINARY_BettingGuildWar_UpdateObserverCount(self, observerCount):
		self.interface.wndMiniMap.UpdateObserverCount(observerCount)

	def __GuildWar_UpdateMemberCount(self, guildID1, memberCount1, guildID2, memberCount2, observerCount):
		guildID1 = int(guildID1)
		guildID2 = int(guildID2)
		memberCount1 = int(memberCount1)
		memberCount2 = int(memberCount2)
		observerCount = int(observerCount)

		self.interface.UpdateMemberCount(guildID1, memberCount1, guildID2, memberCount2)
		self.interface.wndMiniMap.UpdateObserverCount(observerCount)

	if app.ENABLE_GUILDRENEWAL_SYSTEM and app.ENABLE_NEW_WAR_OPTIONS:
		def __GuildWar_OpenAskDialog(self, guildID, warType, winType, ScoreType, TimeType):
			guildName = guild.GetGuildName(guildID)

			# REMOVED_GUILD_BUG_FIX
			if "Noname" == guildName:
				return
			# END_OF_REMOVED_GUILD_BUG_FIX

			import uiGuild
			questionDialog = uiGuild.AcceptGuildWarDialog()
			questionDialog.SAFE_SetAcceptEvent(self.__GuildWar_OnAccept)
			questionDialog.SAFE_SetCancelEvent(self.__GuildWar_OnDecline)
			## [guild_renewal_war]
			questionDialog.Open(guildName, warType, winType, ScoreType, TimeType)

			self.guildWarQuestionDialog = questionDialog
	else:
		def __GuildWar_OpenAskDialog(self, guildID, warType):
			guildName = guild.GetGuildName(guildID)

			# REMOVED_GUILD_BUG_FIX
			if "Noname" == guildName:
				return
			# END_OF_REMOVED_GUILD_BUG_FIX

			import uiGuild
			questionDialog = uiGuild.AcceptGuildWarDialog()
			questionDialog.SAFE_SetAcceptEvent(self.__GuildWar_OnAccept)
			questionDialog.SAFE_SetCancelEvent(self.__GuildWar_OnDecline)
			questionDialog.Open(guildName, warType)

			self.guildWarQuestionDialog = questionDialog

	def __GuildWar_CloseAskDialog(self):
		self.guildWarQuestionDialog.Close()
		self.guildWarQuestionDialog = None

	def __GuildWar_OnAccept(self):

		guildName = self.guildWarQuestionDialog.GetGuildName()

		net.SendChatPacket("/war " + guildName)
		self.__GuildWar_CloseAskDialog()

		return 1

	def __GuildWar_OnDecline(self):

		guildName = self.guildWarQuestionDialog.GetGuildName()

		net.SendChatPacket("/nowar " + guildName)
		self.__GuildWar_CloseAskDialog()

		return 1
	## BINARY CALLBACK
	######################################################################################

	def __HandleMastHP(self, pctHP):
		self.interface.GetMastHpWindow().UpdateMastHp(int(pctHP))

	def __ServerCommand_Build(self):
		serverCommandList={
			"ConsoleEnable"			: self.__Console_Enable,
			"DayMode"				: self.__DayMode_Update,
			"refreshinven"            : self.Update_inventory_ref,
			"update_envanter_lazim"   : self.Update_inventory_lazim,
			"PRESERVE_DayMode"		: self.__PRESERVE_DayMode_Update, 
			"CloseRestartWindow"	: self.__RestartDialog_Close,
			"OpenPrivateShop"		: self.__PrivateShop_Open,
			"PartyHealReady"		: self.PartyHealReady,
			"ShowMeSafeboxPassword"	: self.AskSafeboxPassword,
			"CloseSafebox"			: self.CommandCloseSafebox,	
			#"ITEMZER"				: self.itemselectzer,
			"antiexp"				: self.__antiexp,
			##TEAM_LIST
			"SetTeamOnline"			: self.__TeamLogin,
			"SetTeamOffline"		: self.__TeamLogout,
			##END_OF_TEAM_LIST
			
			#"giftsysshow" 			: self.ZetsuGiftSystem__show__,
			#"giftsyshide" 			: self.ZetsuGiftSystem__hide__,
			#"giftsyseffectshow" 	: self.ZetsuGiftSystem__Effect_show__,
			#"giftsyseffecthide" 	: self.ZetsuGiftSystem__Effect_hide__,			
			#"zetsugfsys" 			: self.ZetsuGiftSystem__init__,	
		
			#inputpowerdziwko
			"get_input_value"		: self.GetInputValue,
			"get_input_start"		: self.GetInputOn,
			"get_input_end"			: self.GetInputOff,
			
			"ReportLogin"			: self.ReportLogin,
			"Report"				: self.Report,	
			
			#"rulet_index"			: self.__Bonuszcserelo,
			#"rulet_index"			: self.__Bonuszcserelo2,		
			
			"getinputbegin"			: self.__Inputget1,
			"getinputend"			: self.__Inputget2,
			
			# BankSystem
			"bank"					: self.RecvBankSystem,
			# END_OF_BankSystem

			##QuestAddons
			"AddQuestButton"		: self.__AddQuestButton,
			##END_OF_QuestAddons

			##Kommunication
			"inputignore"			: self.__InputIgnore,
			"getinput"				: self.__SendTextPacketToQuest,
			##END_OF_Kommunication			
			
			#DEMIRGAME & TURKMMO [P-NEW] PVP SYSTEM
			"demirvidgame"        : self.demirvidgame,
			"demirvid"        : self.demirvid,	
			"demirstartgame"        : self.demirstartgame,
			"demirongame"        : self.demirongame,
			"demirendgame"        : self.demirendgame,  
			"demirwsgame"					: self.demirwsgame,
			"demirwsvidgame"					: self.demirwsgame,
			"demirgogame"					: self.demirgogame,
			"demirgovidgame"					: self.demirgogame,
			"demirwingame"					: self.demirwingame,
			#DEMIRGAME & TURKMMO [P-NEW] PVP SYSTEM			

			# ITEM_MALL
			"CloseMall"				: self.CommandCloseMall,
			"ShowMeMallPassword"	: self.AskMallPassword,
			"item_mall"				: self.__ItemMall_Open,
			# END_OF_ITEM_MALL

			"RefineSuceeded"		: self.RefineSuceededMessage,
			"RefineFailed"			: self.RefineFailedMessage,
			"xmas_snow"				: self.__XMasSnow_Enable,
			"xmas_boom"				: self.__XMasBoom_Enable,
			"xmas_song"				: self.__XMasSong_Enable,
			"xmas_tree"				: self.__XMasTree_Enable,
			"newyear_boom"			: self.__XMasBoom_Enable,
			"PartyRequest"			: self.__PartyRequestQuestion,
			"PartyRequestDenied"	: self.__PartyRequestDenied,
			"horse_state"			: self.__Horse_UpdateState,
			"hide_horse_state"		: self.__Horse_HideState,
			"WarUC"					: self.__GuildWar_UpdateMemberCount,
			"test_server"			: self.__EnableTestServerFlag,
			"mall"			: self.__InGameShop_Show,
			
			"PetEvolution"			: self.SetPetEvolution,
			"PetLevel"				: self.SetPetLevel,
			"PetDuration"			: self.SetPetDuration,
			"PetBonus"				: self.SetPetBonus,
			"PetSkill"				: self.SetPetskill,
			"PetIcon"				: self.SetPetIcon,
			"PetExp"				: self.SetPetExp,
			"PetRarity"				: self.SetPetRarity,
			"PetUnsummon"			: self.PetUnsummon,
			"OpenPetIncubator"		: self.OpenPetIncubator,
			"PetDurationYas"		: self.PetDurationYas,
			"OpenRenamePet"			: self.OpenRenamePet,
			"PetDegrade"			: self.OpenPetDegrade,
			
			#"dragonlair_ranking_open"		: self.OpenDragonLairRanking,
			#"dragonlair_rank"		: self.AddDragonLairRanking,		

			# WEDDING
			"lover_login"			: self.__LoginLover,
			"lover_logout"			: self.__LogoutLover,
			"lover_near"			: self.__LoverNear,
			"lover_far"				: self.__LoverFar,
			"lover_divorce"			: self.__LoverDivorce,
			"PlayMusic"				: self.__PlayMusic,
			# END_OF_WEDDING			

			"OFFMSG"				: self.RecvOfflineMessage,			
			
			# PRIVATE_SHOP_PRICE_LIST
			"MyShopPriceList"		: self.__PrivateShop_PriceList,
			# END_OF_PRIVATE_SHOP_PRICE_LIST	
			"Update"				: self.Update,			
			
			"target_info_respawn_time"	: self.CMD_RecvTargetMonsterRespawnInfo,
			"ds_circle_bonus"		: self.BINARY_DSCircleBonus,
			"shop_sell_tax"			: self.BINARY_ShopSellTax,

			"switcher_start"		: self.OnSwitchbotStart,
			"switcher_stop"			: self.OnSwitchbotStop,
			"switchbot_use"			: self.OnSwitchbotUseSwitcher,
			"switchbot_resume"		: self.OnSwitchbotResume,
			"switchbot_switchers"	: self.OnSwitchbotSwitchers,
		}
		
		if app.ENABLE_CHEQUE_SYSTEM:
			serverCommandList.update({"MyShopPriceListNew"		: self.__PrivateShop_PriceListNew,})		

		if app.ENABLE_HIDE_COSTUME_SYSTEM:
			serverCommandList.update({
				"SetBodyCostumeHidden" : self.SetBodyCostumeHidden,
				"SetHairCostumeHidden" : self.SetHairCostumeHidden,
				"SetAcceCostumeHidden" : self.SetAcceCostumeHidden,
				"SetWeaponCostumeHidden" : self.SetWeaponCostumeHidden,
			})

		self.serverCommander=stringCommander.Analyzer()
		for serverCommandItem in serverCommandList.items():
			self.serverCommander.SAFE_RegisterCallBack(
			serverCommandItem[0], serverCommandItem[1]
			)

		if app.AHMET_FISH_EVENT_SYSTEM:
			self.serverCommander.SAFE_RegisterCallBack( "gc_fish_event_info", self.__OnFishEventCmd )
			self.serverCommander.SAFE_RegisterCallBack( "gc_fish_event_clear", self.__OnFishEventClear )

		self.serverCommander.SAFE_RegisterCallBack("mast_hp", self.__HandleMastHP)

	def OnSwitchbotStart(self, slot):
		if constInfo.switchbotObject:
			constInfo.switchbotObject.BINARY_StartSwitching(int(slot))

	def OnSwitchbotSwitchers(self, flag, value):
		if constInfo.switchbotObject:
			constInfo.switchbotObject.BINARY_UpdateSwitchers(int(flag.split(".")[1]), int(value))

	def OnSwitchbotStop(self, slot):
		if constInfo.switchbotObject:
			constInfo.switchbotObject.BINARY_StopSwitching(int(slot))

	def OnSwitchbotUseSwitcher(self, slot, val):
		if constInfo.switchbotObject:
			constInfo.switchbotObject.BINARY_UpdateUsedAmmount(int(slot), int(val))

	def OnSwitchbotResume(self):
		if constInfo.switchbotObject:
			constInfo.switchbotObject.RestartSwitching()

	def BINARY_DSCircleBonus(self, bonusLevel):
		if self.interface:
			self.interface.ReceiveDSCircleBonus(int(bonusLevel))

	def BINARY_ShopSellTax(self, taxAmmount):
		constInfo.SELL_TAX_AMMOUNT = int(taxAmmount)

	def BINARY_ServerCommand_Run(self, line):
		#dbg.TraceError(line)
		if line.find("PetName") == 0:
			self.SetPetName(line)
			return 1
		try:
			#print " BINARY_ServerCommand_Run", line
			return self.serverCommander.Run(line)
		except RuntimeError, msg:
			dbg.TraceError(msg)
			return 0

	if app.AHMET_FISH_EVENT_SYSTEM:
		def __OnFishEventClear(self):
			self.interface.MiniGameFishClear()

		def __OnFishEventCmd( self, subHeader, firstArg, secondArg ):

			subHeader 	= int( subHeader )
			firstArg 	= int( firstArg )
			secondArg 	= int( secondArg )

			FISH_EVENT_SUBHEADER_TEST 		= 0
			FISH_EVENT_SUBHEADER_BOX_USE 	= 1
			FISH_EVENT_SUBHEADER_SHAPE_ADD 	= 2
			FISH_EVENT_SUBHEADER_GC_REWARD 	= 3
			FISH_EVENT_SUBHEADER_GC_ENABLE 	= 4

			if subHeader == FISH_EVENT_SUBHEADER_BOX_USE:
				self.MiniGameFishUse( firstArg, secondArg )
				return

			if subHeader == FISH_EVENT_SUBHEADER_SHAPE_ADD:
				self.MiniGameFishAdd( firstArg, secondArg )
				return

			if subHeader == FISH_EVENT_SUBHEADER_GC_REWARD:
				self.MiniGameFishReward( firstArg )
				return

			if subHeader == FISH_EVENT_SUBHEADER_GC_ENABLE:
				self.MiniGameFishEvent( firstArg, secondArg )
				return

		def MiniGameFishEvent(self, isEnable, lastUseCount):
			if self.interface:
				self.interface.SetFishEventStatus(isEnable)
				self.interface.MiniGameFishCount(lastUseCount)

		def MiniGameFishUse(self, shape, useCount):
			self.interface.MiniGameFishUse(shape, useCount)
			
		def MiniGameFishAdd(self, pos, shape):
			self.interface.MiniGameFishAdd(pos, shape)
			
		def MiniGameFishReward(self, vnum):
			self.interface.MiniGameFishReward(vnum)	

	def __ProcessPreservedServerCommand(self):
		try:
			command = net.GetPreservedServerCommand()
			while command:
				print " __ProcessPreservedServerCommand", command
				self.serverCommander.Run(command)
				command = net.GetPreservedServerCommand()
		except RuntimeError, msg:
			dbg.TraceError(msg)
			return 0
			
	def ReportLogin(self, id):
		constInfo.ReportLogin = int(id)
		
	def Report(self):
		net.SendQuestInputLongStringPacket(constInfo.ReportEntered)
		
	def __Inputget1(self):
		constInfo.INPUT = 1 

	def __Inputget2(self):
		constInfo.INPUT = 0			

	def PartyHealReady(self):
		self.interface.PartyHealReady()

	def AskSafeboxPassword(self):
		self.interface.AskSafeboxPassword()

	# ITEM_MALL
	def AskMallPassword(self):
		self.interface.AskMallPassword()

	def __ItemMall_Open(self):
		self.interface.OpenItemMall();

	def CommandCloseMall(self):
		self.interface.CommandCloseMall()
	# END_OF_ITEM_MALL

	###def RefineSuceededMessage(self):
	###	snd.PlaySound("sound/ui/make_soket.wav")
	###	self.PopupMessage(localeInfo.REFINE_SUCCESS)
		
	def RefineSuceededMessage(self):
		snd.PlaySound("sound/ui/make_soket.wav")
		self.PopupMessage(localeInfo.REFINE_SUCCESS)
		if app.ENABLE_REFINE_RENEWAL:
			self.interface.CheckRefineDialog(False)
		

	###def RefineFailedMessage(self):
	###	snd.PlaySound("sound/ui/jaeryun_fail.wav")
	###	self.PopupMessage(localeInfo.REFINE_FAILURE)
	
	def RefineFailedMessage(self):
		snd.PlaySound("sound/ui/jaeryun_fail.wav")
		self.PopupMessage(localeInfo.REFINE_FAILURE)
		if app.ENABLE_REFINE_RENEWAL:
			self.interface.CheckRefineDialog(True)
		
		

	def CommandCloseSafebox(self):
		self.interface.CommandCloseSafebox()

	# PRIVATE_SHOP_PRICE_LIST
	def __PrivateShop_PriceList(self, itemVNum, itemPrice):
		uiPrivateShopBuilder.SetPrivateShopItemPrice(itemVNum, itemPrice)	
	# END_OF_PRIVATE_SHOP_PRICE_LIST

	if app.ENABLE_CHEQUE_SYSTEM:
		def __PrivateShop_PriceListNew(self, itemVNum, itemPrice, itemCheque):
			uiPrivateShopBuilder.SetPrivateShopItemPrice(itemVNum, itemPrice)
			uiPrivateShopBuilder.SetPrivateShopItemCheque(itemVNum, itemCheque)	
	
	def SetPetEvolution(self, evo):
		self.petmain.SetEvolution(int(evo))
		self.petmini.SetEvolution(int(evo))

	def OpenPetDegrade(self):
		guildNameBoard = uiCommon.InputDialog()
		guildNameBoard.SetTitle(localeInfo.PET_DEGRADE_TITLE)
		guildNameBoard.SetAcceptEvent(ui.__mem_func__(self.ConfirmPetDegrade))
		guildNameBoard.SetCancelEvent(ui.__mem_func__(self.CancelGuildName))
		guildNameBoard.Open()

		self.guildNameBoard = guildNameBoard

	def ConfirmPetDegrade(self):
		guildName = self.guildNameBoard.GetText()
		if not guildName:
			return False

		try:
			petLevel = int(guildName)
		except:
			return False;

		net.SendChatPacket("/pet_degrade %d" % petLevel)
		self.guildNameBoard.Close()
		self.guildNameBoard = None
		return True

	def OpenRenamePet(self):
		guildNameBoard = uiCommon.InputDialog()
		guildNameBoard.SetTitle(localeInfo.PET_RENAME_TITLE)
		guildNameBoard.SetAcceptEvent(ui.__mem_func__(self.ConfirmPetName))
		guildNameBoard.SetCancelEvent(ui.__mem_func__(self.CancelGuildName))
		guildNameBoard.Open()

		self.guildNameBoard = guildNameBoard
	
	def SetPetName(self, name):
		retName = name.split(" ")[1]
		for i in name.split(" ")[2:]:
			retName += " " + i

		name = retName

		if len(name) > 1 and name != "":
			self.petmini.Show()
		self.petmain.SetName(name)
	
	def SetPetLevel(self, level):
		self.petmain.SetLevel(level)
		self.petmini.SetLevel(int(level))
	
	def SetPetDuration(self, dur, durt):
		if int(durt) > 0:
			self.petmini.SetDuration(dur, durt)
		self.petmain.SetDuration(dur, durt)

		if int(dur) == 0:
			for i in constInfo.SKILL_PET:
				if i != 0:
					self.affectShower.BINARY_NEW_RemoveAffect(i,0)
	
	def SetPetBonus(self, hp, dif, sp):
		self.petmain.SetHp(hp)
		self.petmain.SetDef(dif)
		self.petmain.SetSp(sp)
		
	def SetPetskill(self, slot, idx, lv):
		self.petmini.SetSkill(slot, idx, lv)
		self.petmain.SetSkill(slot, idx, lv)
		if constInfo.SKILL_PET[int(slot)] != int(idx) and constInfo.SKILL_PET[int(slot)] != 0:
			self.affectShower.BINARY_NEW_RemoveAffect(constInfo.SKILL_PET[int(slot)],0)

		if int(idx) > 0:
			self.affectShower.BINARY_NEW_AddAffect(5400+int(idx),int(constInfo.LASTAFFECT_POINT)+1,int(constInfo.LASTAFFECT_VALUE)+1, 0, 0)
		constInfo.SKILL_PET[int(slot)] = 5400 + int(idx)

	def SetPetIcon(self, vnum):
		if int(vnum) > 0:
			self.petmini.SetImageSlot(vnum)
		self.petmain.SetImageSlot(vnum)
		
	def SetPetExp(self, exp, expi, exptot):
		if long(exptot) > 0:
			self.petmini.SetExperience(exp, expi, exptot)
		self.petmain.SetExperience(exp, expi, exptot)

	def SetPetRarity(self, rarity):
		self.petmain.SetRarity(int(rarity))
		
	def PetUnsummon(self):
		self.petmini.SetDefaultInfo()
		self.petmini.Close()
		self.petmain.SetDefaultInfo()
		for i in constInfo.SKILL_PET:
			if i != 0:
				self.affectShower.BINARY_NEW_RemoveAffect(i,0)

		constInfo.SKILL_PET = [0, 0, 0, 0]
	
	def OpenPetMainGui(self):
		self.petmain.Show()
		self.petmain.SetTop()
		
	
	def OpenPetIncubator(self, pet_new = 0):
		import uipetincubatrice
		self.petinc = uipetincubatrice.PetSystemIncubator(pet_new)
		self.petinc.Show()
		self.petinc.SetTop()

	def PetDurationYas(self, vnum):
		pass

	def OpenPetMini(self):
		self.petmini.Show()
		self.petmini.SetTop()
		
	def OpenPetFeed(self):
		
		self.feedwind = uipetfeed.PetFeedWindow()
		self.feedwind.Show()
		self.feedwind.SetTop()

	def Gift_Show(self):
		if constInfo.PET_MAIN == 0:
			self.petmain.Show()
			constInfo.PET_MAIN =1
			self.petmain.SetTop()
		else:
			self.petmain.Hide()
			constInfo.PET_MAIN =0

	def __Horse_HideState(self):
		self.affectShower.SetHorseState(0, 0, 0)

	def __Horse_UpdateState(self, level, health, battery):
		self.affectShower.SetHorseState(int(level), int(health), int(battery))

	def __IsXMasMap(self):
		mapDict = ( "metin2_map_n_flame_01",
					"metin2_map_n_desert_01",
					"metin2_map_spiderdungeon",
					"metin2_map_deviltower1", )

		if background.GetCurrentMapName() in mapDict:
			return False

		return True

	def __XMasSnow_Enable(self, mode):

		self.__XMasSong_Enable(mode)

		if "1"==mode:

			if not self.__IsXMasMap():
				return

			print "XMAS_SNOW ON"
			background.EnableSnow(1)

		else:
			print "XMAS_SNOW OFF"
			background.EnableSnow(0)

	def __XMasBoom_Enable(self, mode):
		if "1"==mode:

			if not self.__IsXMasMap():
				return

			print "XMAS_BOOM ON"
			self.__DayMode_Update("dark")
			self.enableXMasBoom = True
			self.startTimeXMasBoom = app.GetTime()
		else:
			print "XMAS_BOOM OFF"
			self.__DayMode_Update("light")
			self.enableXMasBoom = False

	def __XMasTree_Enable(self, grade):

		print "XMAS_TREE ", grade
		background.SetXMasTree(int(grade))

	def __XMasSong_Enable(self, mode):
		if "1"==mode:
			print "XMAS_SONG ON"

			XMAS_BGM = "xmas.mp3"

			if app.IsExistFile("Data/sound_lib/Sound/" + XMAS_BGM)==1:
				if musicInfo.fieldMusic != "":
					snd.FadeOutMusic("Data/sound_lib/Sound/" + musicInfo.fieldMusic)

				musicInfo.fieldMusic=XMAS_BGM
				snd.FadeInMusic("Data/sound_lib/Sound/" + musicInfo.fieldMusic)

		else:
			print "XMAS_SONG OFF"

			if musicInfo.fieldMusic != "":
				snd.FadeOutMusic("Data/sound_lib/Sound/" + musicInfo.fieldMusic)

			musicInfo.fieldMusic=musicInfo.METIN2THEMA
			snd.FadeInMusic("Data/sound_lib/Sound/" + musicInfo.fieldMusic)

	def __RestartDialog_Close(self):
		self.interface.CloseRestartDialog()

	def __Console_Enable(self):
		constInfo.CONSOLE_ENABLE = True
		self.consoleEnable = True
		app.EnableSpecialCameraMode()
		ui.EnablePaste(True)

	## PrivateShop
	def __PrivateShop_Open(self):
		self.interface.OpenPrivateShopInputNameDialog()

	def BINARY_PrivateShop_Appear(self, vid, text):
		self.interface.AppearPrivateShop(vid, text)

	def BINARY_PrivateShop_Disappear(self, vid):
		self.interface.DisappearPrivateShop(vid)

	## DayMode
	def __PRESERVE_DayMode_Update(self, mode):
		if "light"==mode:
			background.SetEnvironmentData(0)
		elif "dark"==mode:

			if not self.__IsXMasMap():
				return

			background.RegisterEnvironmentData(1, constInfo.ENVIRONMENT_NIGHT)
			background.SetEnvironmentData(1)

	def __DayMode_Update(self, mode):
		if "light"==mode:
			self.curtain.SAFE_FadeOut(self.__DayMode_OnCompleteChangeToLight)
		elif "dark"==mode:

			if not self.__IsXMasMap():
				return

			self.curtain.SAFE_FadeOut(self.__DayMode_OnCompleteChangeToDark)

	def __DayMode_OnCompleteChangeToLight(self):
		background.SetEnvironmentData(0)
		self.curtain.FadeIn()

	def __DayMode_OnCompleteChangeToDark(self):
		background.RegisterEnvironmentData(1, constInfo.ENVIRONMENT_NIGHT)
		background.SetEnvironmentData(1)
		self.curtain.FadeIn()

	## XMasBoom
	def __XMasBoom_Update(self):

		self.BOOM_DATA_LIST = ( (2, 5), (5, 2), (7, 3), (10, 3), (20, 5) )
		if self.indexXMasBoom >= len(self.BOOM_DATA_LIST):
			return

		boomTime = self.BOOM_DATA_LIST[self.indexXMasBoom][0]
		boomCount = self.BOOM_DATA_LIST[self.indexXMasBoom][1]

		if app.GetTime() - self.startTimeXMasBoom > boomTime:

			self.indexXMasBoom += 1

			for i in xrange(boomCount):
				self.__XMasBoom_Boom()

	def __XMasBoom_Boom(self):
		x, y, z = player.GetMainCharacterPosition()
		randX = app.GetRandom(-150, 150)
		randY = app.GetRandom(-150, 150)

		snd.PlaySound3D(x+randX, -y+randY, z, "sound/common/etc/salute.mp3")

	def __PartyRequestQuestion(self, vid):
		vid = int(vid)
		partyRequestQuestionDialog = uiCommon.QuestionDialog()
		partyRequestQuestionDialog.SetText(chr.GetNameByVID(vid) + localeInfo.PARTY_DO_YOU_ACCEPT)
		partyRequestQuestionDialog.SetAcceptText(localeInfo.UI_ACCEPT)
		partyRequestQuestionDialog.SetCancelText(localeInfo.UI_DENY)
		partyRequestQuestionDialog.SetAcceptEvent(lambda arg=True: self.__AnswerPartyRequest(arg))
		partyRequestQuestionDialog.SetCancelEvent(lambda arg=False: self.__AnswerPartyRequest(arg))
		partyRequestQuestionDialog.Open()
		partyRequestQuestionDialog.vid = vid
		self.partyRequestQuestionDialog = partyRequestQuestionDialog

	def __AnswerPartyRequest(self, answer):
		if not self.partyRequestQuestionDialog:
			return

		vid = self.partyRequestQuestionDialog.vid

		if answer:
			net.SendChatPacket("/party_request_accept " + str(vid))
		else:
			net.SendChatPacket("/party_request_deny " + str(vid))

		self.partyRequestQuestionDialog.Close()
		self.partyRequestQuestionDialog = None

	def __PartyRequestDenied(self):
		self.PopupMessage(localeInfo.PARTY_REQUEST_DENIED)

	def __EnableTestServerFlag(self):
		app.EnableTestServerFlag()

	def __InGameShop_Show(self, url):
		if constInfo.IN_GAME_SHOP_ENABLE:
			self.interface.OpenWebWindow(url)


	def ManagerTickets(self, cmd):
		cmd = cmd.split('#')
		if cmd[0] == 'QID':
			constInfo.Tickets['QID'] = int(cmd[1])
		elif cmd[0] == 'INPUT':
			constInfo.INPUT_IGNORE = int(cmd[1])
		elif cmd[0] == 'SEND':
			net.SendQuestInputLongStringPacket(str(constInfo.Tickets['QCMD']))
			constInfo.Tickets['QCMD'] = ''
		elif cmd[0] == 'CLEAR_CONTENT':
			constInfo.Tickets['MY_TICKETS'] = []
			constInfo.Tickets['GLOBAL_TICKETS'] = []
		elif cmd[0] == 'CLEAR_PERMISIONS':
			constInfo.Tickets['PERMISIONS'] = []
		elif cmd[0] == 'SET_TICKET':
			date = cmd[4].split('[_]')
			constInfo.Tickets['GLOBAL_TICKETS'].append([cmd[1], cmd[2].replace('[_]', ' '), int(cmd[3]), date[0], date[1], int(cmd[5]), cmd[6], cmd[7].replace('[_]', ' '), int(cmd[8])])
			if cmd[6] == player.GetName():
				constInfo.Tickets['MY_TICKETS'].append([cmd[1], cmd[2].replace('[_]', ' '), int(cmd[3]), date[0], date[1], int(cmd[5]), cmd[6], cmd[7].replace('[_]', ' '), int(cmd[8])])
		elif cmd[0] == 'CREATE_ANSWER':
			constInfo.Tickets['ANSWERS'][cmd[1]] = []
		elif cmd[0] == 'SET_ANSWER':
			date = cmd[3].split('[_]')
			constInfo.Tickets['ANSWERS'][cmd[1]].append([cmd[2], date[0], date[1], cmd[4].replace('[_]', ' ')])
		elif cmd[0] == 'SET_PERMISION':
			constInfo.Tickets['PERMISIONS'].append([cmd[1], int(cmd[2]), int(cmd[3]), int(cmd[4])])
		elif cmd[0] == 'OPEN':
			self.interface.wndTicket.Open(int(cmd[1]))
		elif cmd[0] == 'REFRESH_CONTENT':
			self.interface.wndTicket.RefreshPage()					
			
	def __ArayuzManager(self):
		if constInfo.arayuzkoray == 0:
			self.interface.HideAllWindows()
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Kitakar?")
			constInfo.arayuzkoray = 1
		elif constInfo.arayuzkoray == 1:
			self.interface.wndTaskBar.Show()
			self.interface.wndChat.Show()
			self.interface.wndMiniMap.Show()
			try: self.interface.wndEnergyBar.Show()
			except: pass
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Kitakar? nem akt?")
			constInfo.arayuzkoray = 0					

	#DEMIRGAME & TURKMMO [P-NEW] PVP SYSTEM
	def demirvidgame(self, id):
		import constInfo
		constInfo.demirvidgame = int(id)
		
	def demirongame(self):
		constInfo.INPUT_IGNORE = 1
        
	def demirendgame(self):
		constInfo.INPUT_IGNORE = 0
			
	def demirstartgame(self):
		net.SendQuestInputStringPacket(str(constInfo.demirstartgame))
		
	def demirvid(self, id):
		constInfo.demirvid = int(id)
		
	def OpenQuestWindow(self, skin, idx):
		if constInfo.CApiSetHide == 1:
			net.SendQuestInputStringPacket(str(constInfo.SendString))
			constInfo.CApiSetHide = 0
			return		
		if constInfo.INPUT_IGNORE == 1:
			return
		else:
			self.interface.OpenQuestWindow(skin, idx)		
			
	##QuestAddons
	def __AddQuestButton(self, qt='', qi=''):
		if qt != '' and qi != '' and qi.isdigit():
			constInfo.QuestButtonsDict[qt] = int(qi)
	##END_OF_QuestAddons

	##GetInput
	def __InputIgnore(self, flag):
		if flag.isdigit() and flag in map(str, range(2)):
			constInfo.INPUT_IGNORE = int(flag)#int b'coz bool is not available in Py2.2.15 only 2.2.3 or newer

	def __SendTextPacketToQuest(self):
		net.SendQuestInputStringPacket(localeInfo.SEND_BACK)
		localeInfo.SEND_BACK = ""
	##END_OF_GetInput

	##BankSystem
	def RecvBankSystem(self, recv):
		_debug(recv)
		args = recv.split("|")
		cmd = args.pop(0)
		if cmd == "open":
			if args[0].lower() in ["true", "false"]:
				self.interface.Bank_Open(eval(args[0].lower().capitalize()))
			else:
				dbg.TraceError("GameWindow.RecvBankSystem - Unknown \"open\" subcommand: \""+str(args[0])+"\"")
		elif cmd == "setmoney":
			if args[0].isdigit():
				self.interface.Bank_SetMoney(args[0])
			else:
				dbg.TraceError("GameWindow.RecvBankSystem - Unknown \"setmoney\" Gold format: \""+str(args[0])+"\"")
		elif cmd == "changepage":
			self.interface.Bank_ChangePage(str(args[0]))
		elif cmd == "message":
			#args[0] = ActType | args[1] = Message
			if args[0].upper() in ["ERROR","OK","UNKNOWN", "WARNING"]:
				self.interface.Bank_MakePopupDialog(args[0].upper(), args[1].replace("_", " "))
			else:
				dbg.TraceError("GameWindow.RecvBankSystem - Unknown \"message\" ActType: \""+str(args[0])+"\"")
		else:
			dbg.TraceError("GameWindow.RecvBankSystem - Unknown command: \""+str(args[0])+"\"")
	##END_OF_BankSystem			
			
	def demirwsgame(self):
		net.SendChatPacket("(demirwsgame)")
		return
		
	def demirgogame(self):
		net.SendChatPacket("(demirgogame)")
		return
		
	def demirwingame(self):
		net.SendChatPacket("(demirwingame)")
		return
			
	def __Inputget1(self):
		constInfo.INPUT_IGNORE = 1 
			
	def __Inputget2(self):
		constInfo.INPUT_IGNORE = 0	
		
	# PET_INVENTORY
	#def __PetIsMineByVid(self, vid):
	#	targetName = chr.GetNameByVID(int(vid))
	#	charName = player.GetName() or chr.GetMainCharacterName()
	#	if targetName[0:len(charName)] == charName:
	#		localeInfo.SEND_BACK = "true"
	#	else:
	#		localeInfo.SEND_BACK = "false"
    #
	#	self.__SendTextPacketToQuest()
	#	localeInfo.SEND_BACK = ""
    #
	#def __SendTextPacketToQuest(self):
	#	net.SendQuestInputStringPacket(localeInfo.SEND_BACK)
	#	
	#def __PressXKey(self):
	#	import event
	#	#self.__DeactivarGui()
	#	self.__PetHide()
	#	event.QuestButtonClick(constInfo2.PET_SEND_AWAY_BUTTON_INDEX)
	#	
	#def GetInputStringStart(self):
	#	constInfo.INPUT_IGNORE = 1
    #
	#def GetInputStringEnd(self):
	#	constInfo.INPUT_IGNORE = 0		
	#	
	#def __PetSetClearItemSlotButtonIndex(self, index):
	#	constInfo2.PET_CLEAR_ITEM_SLOT_BUTTON_INDEX = int(index)
    #
	#def __PetSetIncreaseBoniButtonIndex(self, index):
	#	constInfo2.PET_INCREASE_BONI_BUTTON_INDEX = int(index)
    #
	#def __PetSetSendAwayButtonIndex(self, index):
	#	constInfo2.PET_SEND_AWAY_BUTTON_INDEX = int(index)
	#	
	#def __ActivarGui(self):
	#	global pet_gui_activado
	#	pet_gui_activado = 1
	#	
	#def __DeactivarGui(self):
	#	global pet_gui_activado
	#	pet_gui_activado = 0	
	#	
	#def __PetShow(self):
	#	if not self.petInventoryWnd:
	#		import uiPet
	#		self.petInventoryWnd = uiPet.PetInventoryDialog()
	#	self.petInventoryWnd.Show()
    #
	#def __PetHide(self):
	#	if self.petInventoryWnd:
	#		self.petInventoryWnd.Hide()
    #
	#def __PetGetClearSlot(self):
	#	net.SendQuestInputStringPacket(str(self.petInventoryWnd.GetClearSlot()))
    #
	#def __PetGetIncreaseBoni(self):
	#	net.SendQuestInputStringPacket(str(self.petInventoryWnd.GetIncreaseBoni()))
    #
	#def __PetSet(self, itemVnum):
	#	if not self.petInventoryWnd:
	#		import uiPet
	#		self.petInventoryWnd = uiPet.PetInventoryDialog()
	#	self.petInventoryWnd.SetPet(itemVnum)
    #
	#def __PetSetHead(self, itemVnum):
	#	if not self.petInventoryWnd:
	#		import uiPet
	#		self.petInventoryWnd = uiPet.PetInventoryDialog()
	#	if int(itemVnum) > 0:
	#		self.petInventoryWnd.SetHeadItem(itemVnum)
	#	else:
	#		self.petInventoryWnd.ClearHeadItem()
    #
	#def __PetSetNeck(self, itemVnum):
	#	if not self.petInventoryWnd:
	#		import uiPet
	#		self.petInventoryWnd = uiPet.PetInventoryDialog()
	#	if int(itemVnum) > 0:
	#		self.petInventoryWnd.SetNeckItem(itemVnum)
	#	else:
	#		self.petInventoryWnd.ClearNeckItem()
    #
	#def __PetSetFoot(self, itemVnum):
	#	if not self.petInventoryWnd:
	#		import uiPet
	#		self.petInventoryWnd = uiPet.PetInventoryDialog()
	#	if int(itemVnum) > 0:
	#		self.petInventoryWnd.SetFootItem(itemVnum)
	#	else:
	#		self.petInventoryWnd.ClearFootItem()
    #
	#def __PetSetAttackValue(self, value):
	#	if not self.petInventoryWnd:
	#		import uiPet
	#		self.petInventoryWnd = uiPet.PetInventoryDialog()
	#	self.petInventoryWnd.SetAttackValue(value)
    #
	#def __PetSetMagicAttackValue(self, value):
	#	if not self.petInventoryWnd:
	#		import uiPet
	#		self.petInventoryWnd = uiPet.PetInventoryDialog()
	#	self.petInventoryWnd.SetMagicAttackValue(value)
    #
	#def __PetSetArmorValue(self, value):
	#	if not self.petInventoryWnd:
	#		import uiPet
	#		self.petInventoryWnd = uiPet.PetInventoryDialog()
	#	self.petInventoryWnd.SetArmorValue(value)
    #
	#def __PetSetName(self, name):
	#	if not self.petInventoryWnd:
	#		import uiPet
	#		self.petInventoryWnd = uiPet.PetInventoryDialog()
	#	self.petInventoryWnd.SetName(name.replace("[_]", " "))
    #
	#def __PetSetLevel(self, level):
	#	if not self.petInventoryWnd:
	#		import uiPet
	#		self.petInventoryWnd = uiPet.PetInventoryDialog()
	#	self.petInventoryWnd.SetLevel(level)
    #
	#def __PetSetExp(self, exp):
	#	if not self.petInventoryWnd:
	#		import uiPet
	#		self.petInventoryWnd = uiPet.PetInventoryDialog()
	#	self.petInventoryWnd.SetExp(exp)
	#	self.petInventoryWnd.UpdateExpBar()
    #
	#def __PetSetMaxExp(self, maxexp):
	#	if not self.petInventoryWnd:
	#		import uiPet
	#		self.petInventoryWnd = uiPet.PetInventoryDialog()
	#	self.petInventoryWnd.SetMaxExp(maxexp)
	#	self.petInventoryWnd.UpdateExpBar()
    #
	#def __PetSetSkillPoints(self, points):
	#	if not self.petInventoryWnd:
	#		import uiPet
	#		self.petInventoryWnd = uiPet.PetInventoryDialog()
	#	self.petInventoryWnd.SetSkillPoints(points)	
	#	
	# Pet invertory vége
	
	def GetInputOn(self):
		constInfo.INPUT_IGNORE = 1
	
	def GetInputOff(self):
		constInfo.INPUT_IGNORE = 0
	
	def GetInputValue(self):
		net.SendQuestInputStringPacket(str(constInfo.VID))
			
	if app.ADD_INVENTORY:	
		def Update_inventory_ref(self):
			if self.interface:
				self.interface.SetInventoryPageKilit()
				
		def Update_inventory_lazim(self, lazim):
			self.wndPopupDialog = uiCommon.PopupDialog()
			self.wndPopupDialog.SetText(lazim + " " + localeInfo.ENVANTER_ANAH_LAZIM)
			self.wndPopupDialog.Open()
		
	# WEDDING
	def __LoginLover(self):
		if self.interface.wndMessenger:
			self.interface.wndMessenger.OnLoginLover()

	def __LogoutLover(self):
		if self.interface.wndMessenger:
			self.interface.wndMessenger.OnLogoutLover()
		if self.affectShower:
			self.affectShower.HideLoverState()

	def __LoverNear(self):
		if self.affectShower:
			self.affectShower.ShowLoverState()

	def __LoverFar(self):
		if self.affectShower:
			self.affectShower.HideLoverState()

	def __LoverDivorce(self):
		if self.interface.wndMessenger:
			self.interface.wndMessenger.ClearLoverInfo()
		if self.affectShower:
			self.affectShower.ClearLoverState()

	def __PlayMusic(self, flag, filename):
		flag = int(flag)
		if flag:
			snd.FadeOutAllMusic()
			musicInfo.SaveLastPlayFieldMusic()
			snd.FadeInMusic("Data/sound_lib/Sound/" + filename)
		else:
			snd.FadeOutAllMusic()
			musicInfo.LoadLastPlayFieldMusic()
			snd.FadeInMusic("Data/sound_lib/Sound/" + musicInfo.fieldMusic)	
			
	def Update(self, ch):
		import serverInfo
		net.SetServerInfo("%s, CH%s" % (serverInfo.SERVER_NAME, str(ch)))
		constInfo.ch = int(ch)
				
	## Begin LuckyBoxes system
	def ZetsuGiftSystem__init__(self, index):   
		constInfo.GIFTSYS = index # Eger Çalişmaz ise Degiştir:   constInfo.GIFTSYS = int(index)
		
	def ZetsuGiftSystem__deff__(self):
		event.QuestButtonClick(int(constInfo.GIFTSYS))
		
    ## End LuckyBoxes
    # Warning!! Let the last row empty!! ##
	def ZetsuGiftSystem__show__(self):
		self.GiftBox.Show()
		
	def ZetsuGiftSystem__Effect_show__(self):	
		net.SendChatPacket("(giftboxshoweffect)")
		return	
		
	def ZetsuGiftSystem__Effect_hide__(self):	
		net.SendChatPacket("(giftboxhideeffect)")
		return	
		
	def ZetsuGiftSystem__hide__(self):
		self.GiftBox.Hide()
					
			
	if app.ENABLE_CHANGELOOK_SYSTEM:
		def ActChangeLook(self, iAct):
			if self.interface:
				self.interface.ActChangeLook(iAct)

		def AlertChangeLook(self):
			self.PopupMessage(localeInfo.CHANGE_LOOK_DEL_ITEM)			
			
	def RecvOfflineMessage(self, x):
		txt = str(x)
		nick = txt.split("_")[0]
		zamanex = txt.split("_")[1]
		mesaj = txt.split("_")[2]
		mesaj = mesaj.replace("$", " ")

		import datetime
		zaman = datetime.datetime.fromtimestamp(int(zamanex)).strftime('%d-%m-%Y %H:%M:%S')

		chat.AppendWhisper(chat.WHISPER_TYPE_CHAT, nick, "|cffff0000|H|h[OFF.?ENET-%s]:|h|r %s" % (zaman, mesaj))
		self.interface.RecvWhisper(nick)			
			
	if app.ENABLE_SASH_SYSTEM:
		def ActSash(self, iAct, bWindow):
			if self.interface:
				self.interface.ActSash(iAct, bWindow)

		def AlertSash(self, bWindow):
			snd.PlaySound("sound/ui/make_soket.wav")
			if bWindow:
				self.PopupMessage(localeInfo.SASH_DEL_SERVEITEM)
			else:
				self.PopupMessage(localeInfo.SASH_DEL_ABSORDITEM)

	# System Anti Exp - Start
	def __antiexp(self, qid):
		constInfo.antiexp= int(qid)
	# System Anti Exp - End		

	#def __switch_channel(self):
	#	import uiChannel
	#	a = uiChannel.ChannelChanger()
	#	a.Show()
	
	####Mijago switch
	def __Bonuszcserelo2(self):
		if self.switchbot.bot_shown == 1:
			self.switchbot.Hide()
		else:
			self.switchbot.Show()
	####################
	
	# TEAM_LIST
	def __TeamLogin(self, name):
		if self.interface.wndMessenger:
			self.interface.wndMessenger.OnLoginTeam(name)

	def __TeamLogout(self, name):
		if self.interface.wndMessenger:
			self.interface.wndMessenger.OnLogoutTeam(name)
	# END_OF_TEAM_LIST
	if app.ENABLE_FISH_EVENT:
		def MiniGameFishEvent(self, isEnable, lasUseCount):
			if self.interface:
				self.interface.SetFishEventStatus(isEnable)
				self.interface.MiniGameFishCount(lasUseCount)
				self.interface.IntegrationEventBanner()

		def MiniGameFishUse(self, shape, useCount):
			self.interface.MiniGameFishUse(shape, useCount)
			
		def MiniGameFishAdd(self, pos, shape):
			self.interface.MiniGameFishAdd(pos, shape)
			
		def MiniGameFishReward(self, vnum):
			self.interface.MiniGameFishReward(vnum)

	if app.ENABLE_SHOW_CHEST_DROP:
		def BINARY_AddChestDropInfo(self, chestVnum, pageIndex, slotIndex, itemVnum, itemCount):
			if self.interface:
				self.interface.AddChestDropInfo(chestVnum, pageIndex, slotIndex, itemVnum, itemCount)
						
		def BINARY_RefreshChestDropInfo(self, chestVnum):
			if self.interface:
				self.interface.RefreshChestDropInfo(chestVnum)
